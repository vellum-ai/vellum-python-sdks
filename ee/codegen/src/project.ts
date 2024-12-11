import { exec } from "child_process";
import fs from "fs";
import { mkdir } from "fs/promises";
import { join } from "path";

import { python } from "@fern-api/python-ast";
import { Comment } from "@fern-api/python-ast/Comment";
import { StarImport } from "@fern-api/python-ast/StarImport";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_DISPLAY_NODE_MODULE_PATH,
  GENERATED_NODES_MODULE_NAME,
  GENERATED_NODES_PATH,
} from "./constants";
import { createNodeContext, WorkflowContext } from "./context";
import { InputVariableContext } from "./context/input-variable-context";
import { InitFile, Inputs, Workflow } from "./generators";
import { ProjectSerializationError } from "./generators/errors";
import { BaseNode } from "./generators/nodes/bases";
import { GuardrailNode } from "./generators/nodes/guardrail-node";
import { InlineSubworkflowNode } from "./generators/nodes/inline-subworkflow-node";
import { SearchNode } from "./generators/nodes/search-node";
import { TemplatingNode } from "./generators/nodes/templating-node";

import { codegen } from "./index";

import { ApiNodeContext } from "src/context/node-context/api-node";
import { BaseNodeContext } from "src/context/node-context/base";
import { CodeExecutionContext } from "src/context/node-context/code-execution-node";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { ErrorNodeContext } from "src/context/node-context/error-node";
import { FinalOutputNodeContext } from "src/context/node-context/final-output-node";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GuardrailNodeContext } from "src/context/node-context/guardrail-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { InlineSubworkflowNodeContext } from "src/context/node-context/inline-subworkflow-node";
import { MapNodeContext } from "src/context/node-context/map-node";
import { MergeNodeContext } from "src/context/node-context/merge-node";
import { NoteNodeContext } from "src/context/node-context/note-node";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { TextSearchNodeContext } from "src/context/node-context/text-search-node";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { ApiNode } from "src/generators/nodes/api-node";
import { CodeExecutionNode } from "src/generators/nodes/code-execution-node";
import { ConditionalNode } from "src/generators/nodes/conditional-node";
import { ErrorNode } from "src/generators/nodes/error-node";
import { FinalOutputNode } from "src/generators/nodes/final-output-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import { InlinePromptNode } from "src/generators/nodes/inline-prompt-node";
import { MapNode } from "src/generators/nodes/map-node";
import { MergeNode } from "src/generators/nodes/merge-node";
import { NoteNode } from "src/generators/nodes/note-node";
import { PromptDeploymentNode } from "src/generators/nodes/prompt-deployment-node";
import { SubworkflowDeploymentNode } from "src/generators/nodes/subworkflow-deployment-node";
import { WorkflowVersionExecConfigSerializer } from "src/serializers/vellum";
import {
  EntrypointNode,
  WorkflowDataNode,
  WorkflowNodeType as WorkflowNodeTypeEnum,
  WorkflowVersionExecConfig,
} from "src/types/vellum";
import { getNodeId } from "src/utils/nodes";
import { assertUnreachable } from "src/utils/typing";

export declare namespace WorkflowProjectGenerator {
  interface BaseArgs {
    moduleName: string;
  }

  interface BaseProject extends BaseArgs {
    absolutePathToOutputDirectory: string;
    workflowsSdkModulePath?: readonly string[];
    workflowVersionExecConfigData: unknown;
    vellumApiKey?: string;
  }

  interface NestedProject extends BaseArgs {
    workflowContext: WorkflowContext;
    workflowVersionExecConfig: WorkflowVersionExecConfig;
  }

  type Args = BaseProject | NestedProject;
}

export class WorkflowProjectGenerator {
  public readonly workflowVersionExecConfig: WorkflowVersionExecConfig;
  private readonly workflowContext: WorkflowContext;

  constructor({ moduleName, ...rest }: WorkflowProjectGenerator.Args) {
    if ("workflowContext" in rest) {
      this.workflowContext = rest.workflowContext;
      this.workflowVersionExecConfig = rest.workflowVersionExecConfig;
    } else {
      const workflowVersionExecConfigResult =
        WorkflowVersionExecConfigSerializer.parse(
          rest.workflowVersionExecConfigData,
          {
            allowUnrecognizedUnionMembers: true,
            allowUnrecognizedEnumValues: true,
            unrecognizedObjectKeys: "strip",
          }
        );
      if (!workflowVersionExecConfigResult.ok) {
        const { errors } = workflowVersionExecConfigResult;
        if (errors.length) {
          throw new ProjectSerializationError(
            `Invalid Workflow Version exec config. Found ${
              errors.length
            } errors, including:
${errors.slice(0, 3).map((err) => {
  return `- ${err.message} at ${err.path.join(".")}`;
})}`
          );
        } else {
          throw new ProjectSerializationError(
            "Invalid workflow version exec config, but no errors were returned."
          );
        }
      }
      const vellumApiKey = rest.vellumApiKey ?? process.env.VELLUM_API_KEY;
      if (!vellumApiKey) {
        throw new ProjectSerializationError(
          "No workspace API key provided or found in environment variables."
        );
      }

      this.workflowVersionExecConfig = workflowVersionExecConfigResult.value;
      const rawEdges = this.workflowVersionExecConfig.workflowRawData.edges;

      const workflowClassName =
        this.workflowVersionExecConfig.workflowRawData.definition?.name ||
        "Workflow";

      this.workflowContext = new WorkflowContext({
        workflowsSdkModulePath: rest.workflowsSdkModulePath,
        absolutePathToOutputDirectory: rest.absolutePathToOutputDirectory,
        moduleName,
        workflowClassName,
        vellumApiKey,
        workflowRawEdges: rawEdges,
      });
    }
  }

  public getModuleName(): string {
    return this.workflowContext.moduleName;
  }

  public async generateCode(): Promise<void> {
    const { inputs, workflow, nodes } = await this.generateAssets();

    const absolutePathToModuleDirectory = join(
      this.workflowContext.absolutePathToOutputDirectory,
      this.workflowContext.moduleName
    );

    await mkdir(absolutePathToModuleDirectory, {
      recursive: true,
    });

    await Promise.all([
      // __init__.py
      this.generateRootInitFile().persist(),
      // display/__init__.py
      this.generateDisplayRootInitFile().persist(),
      // display/workflow.py
      workflow.getWorkflowDisplayFile().persist(),
      // inputs.py
      inputs.persist(),
      // workflow.py
      workflow.getWorkflowFile().persist(),
      // nodes/*
      ...this.generateNodeFiles(nodes),
    ]);

    const setupCfgPath = this.resolvePythonConfigFilePath();
    const isortCmd = process.env.ISORT_CMD ?? "isort";

    await new Promise((resolve, reject) => {
      exec(
        `${isortCmd} --sp ${setupCfgPath} ${this.workflowContext.absolutePathToOutputDirectory}`,
        (error: Error | null) => {
          if (error) {
            reject(error);
          } else {
            resolve(undefined);
          }
        }
      );
    });
  }

  private generateRootInitFile(): InitFile {
    const statements: AstNode[] = [];
    const imports: StarImport[] = [];
    const comments: Comment[] = [];

    const parentNode = this.workflowContext.parentNode;
    if (parentNode) {
      statements.push(parentNode.generateNodeClass());
    } else {
      comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      imports.push(
        python.starImport({
          modulePath: [
            this.workflowContext.moduleName,
            GENERATED_DISPLAY_MODULE_NAME,
          ],
        })
      );
    }

    const rootInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? [...this.workflowContext.parentNode.getNodeModulePath()]
        : [this.workflowContext.moduleName],
      statements,
      imports,
      comments,
    });

    return rootInitFile;
  }

  private generateDisplayRootInitFile(): InitFile {
    const statements: AstNode[] = [];
    const imports: StarImport[] = [];
    const comments: Comment[] = [];

    const parentNode = this.workflowContext.parentNode;
    if (parentNode) {
      statements.push(...parentNode.generateNodeDisplayClasses());
      comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      imports.push(
        python.starImport({
          modulePath: [...parentNode.getNodeDisplayModulePath(), "nodes"],
        })
      );
      imports.push(
        python.starImport({
          modulePath: [...parentNode.getNodeDisplayModulePath(), "workflow"],
        })
      );
    } else {
      comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      imports.push(
        python.starImport({
          modulePath: [
            this.workflowContext.moduleName,
            GENERATED_DISPLAY_MODULE_NAME,
            "nodes",
          ],
        })
      );
      imports.push(
        python.starImport({
          modulePath: [
            this.workflowContext.moduleName,
            GENERATED_DISPLAY_MODULE_NAME,
            "workflow",
          ],
        })
      );
    }

    const rootDisplayInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? [...this.workflowContext.parentNode.getNodeDisplayModulePath()]
        : [this.workflowContext.moduleName, GENERATED_DISPLAY_MODULE_NAME],
      statements,
      imports,
      comments,
    });

    return rootDisplayInitFile;
  }

  private async generateAssets(): Promise<{
    inputs: Inputs;
    workflow: Workflow;
    nodes: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[];
  }> {
    const moduleName = this.workflowContext.moduleName;

    this.workflowVersionExecConfig.inputVariables.forEach((inputVariable) => {
      const inputVariableContext = new InputVariableContext({
        inputVariableData: inputVariable,
        workflowContext: this.workflowContext,
      });
      this.workflowContext.addInputVariableContext(inputVariableContext);
    });

    let entrypointNode: EntrypointNode | undefined;
    const nodesToGenerate: WorkflowDataNode[] = [];
    await Promise.all(
      this.workflowVersionExecConfig.workflowRawData.nodes.map(
        async (nodeData) => {
          if (nodeData.type === "TERMINAL") {
            this.workflowContext.addWorkflowOutputContext(
              new WorkflowOutputContext({
                terminalNodeData: nodeData,
              })
            );
          } else if (nodeData.type === "ENTRYPOINT") {
            if (entrypointNode) {
              throw new Error("Multiple entrypoint nodes found");
            }
            entrypointNode = nodeData;
            return;
          }

          nodesToGenerate.push(nodeData);

          const nodeContext = await createNodeContext({
            workflowContext: this.workflowContext,
            nodeData,
          });
          this.workflowContext.addNodeContext(nodeContext);
        }
      )
    );
    if (!entrypointNode) {
      throw new Error("Entrypoint node not found");
    }
    this.workflowContext.addEntrypointNode(entrypointNode);

    const inputs = codegen.inputs({
      workflowContext: this.workflowContext,
    });

    const nodeIds = nodesToGenerate.map((nodeData) => getNodeId(nodeData));
    const nodes = this.generateNodes(nodeIds);

    const workflow = codegen.workflow({
      moduleName,
      workflowContext: this.workflowContext,
      inputs,
      nodes: nodesToGenerate,
      displayData: this.workflowVersionExecConfig.workflowRawData.displayData,
    });

    return { inputs, workflow, nodes };
  }

  private generateNodes(
    nodeIds: string[]
  ): BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[] {
    const nodes: BaseNode<
      WorkflowDataNode,
      BaseNodeContext<WorkflowDataNode>
    >[] = [];

    nodeIds.forEach(async (nodeId) => {
      let node: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;

      const nodeContext = this.workflowContext.getNodeContext(nodeId);
      const nodeData = nodeContext.nodeData;

      const nodeType = nodeData.type;
      switch (nodeType) {
        case WorkflowNodeTypeEnum.SEARCH: {
          node = new SearchNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as TextSearchNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.SUBWORKFLOW: {
          const variant = nodeData.data.variant;
          switch (variant) {
            case "INLINE":
              node = new InlineSubworkflowNode({
                workflowContext: this.workflowContext,
                nodeContext: nodeContext as InlineSubworkflowNodeContext,
              });
              break;
            case "DEPLOYMENT":
              node = new SubworkflowDeploymentNode({
                workflowContext: this.workflowContext,
                nodeContext: nodeContext as SubworkflowDeploymentNodeContext,
              });
              break;
            default: {
              assertUnreachable(variant);
            }
          }
          break;
        }
        case WorkflowNodeTypeEnum.MAP: {
          const mapNodeVariant = nodeData.data.variant;
          switch (mapNodeVariant) {
            case "INLINE":
              node = new MapNode({
                workflowContext: this.workflowContext,
                nodeContext: nodeContext as MapNodeContext,
              });
              break;
            case "DEPLOYMENT":
              throw new Error(`DEPLOYMENT variant not yet supported`);
            default: {
              assertUnreachable(mapNodeVariant);
            }
          }
          break;
        }
        case WorkflowNodeTypeEnum.METRIC: {
          node = new GuardrailNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as GuardrailNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.CODE_EXECUTION: {
          node = new CodeExecutionNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as CodeExecutionContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.PROMPT: {
          const promptNodeVariant = nodeData.data.variant;

          switch (promptNodeVariant) {
            case "INLINE":
              node = new InlinePromptNode({
                workflowContext: this.workflowContext,
                nodeContext: nodeContext as InlinePromptNodeContext,
              });
              break;
            case "DEPLOYMENT":
              node = new PromptDeploymentNode({
                workflowContext: this.workflowContext,
                nodeContext: nodeContext as PromptDeploymentNodeContext,
              });
              break;
            case "LEGACY":
              throw new Error(
                `LEGACY variant should have been converted to INLINE variant by this point.`
              );
            default: {
              assertUnreachable(promptNodeVariant);
            }
          }
          break;
        }
        case WorkflowNodeTypeEnum.TEMPLATING: {
          node = new TemplatingNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as TemplatingNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.CONDITIONAL: {
          node = new ConditionalNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as ConditionalNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.TERMINAL: {
          node = new FinalOutputNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as FinalOutputNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.MERGE: {
          node = new MergeNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as MergeNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.ERROR: {
          node = new ErrorNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as ErrorNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.NOTE: {
          node = new NoteNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as NoteNodeContext,
          });
          break;
        }
        case WorkflowNodeTypeEnum.API:
          node = new ApiNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as ApiNodeContext,
          });
          break;
        case WorkflowNodeTypeEnum.GENERIC:
          node = new GenericNode({
            workflowContext: this.workflowContext,
            nodeContext: nodeContext as GenericNodeContext,
          });
          break;
        default: {
          throw new Error(`Unsupported node type: ${nodeType}`);
        }
      }

      nodes.push(node);
    });

    return nodes;
  }

  private generateNodeFiles(
    nodes: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[]
  ): Promise<unknown>[] {
    const rootNodesInitFileStatements: AstNode[] = [];
    const rootDisplayNodesInitFileStatements: AstNode[] = [];
    if (nodes.length) {
      const nodeInitFileAllField = python.field({
        name: "__all__",
        initializer: python.TypeInstantiation.list([
          ...nodes.map((node) => {
            return python.TypeInstantiation.str(node.getNodeClassName());
          }),
        ]),
      });
      rootNodesInitFileStatements.push(nodeInitFileAllField);

      const nodeDisplayInitFileAllField = python.field({
        name: "__all__",
        initializer: python.TypeInstantiation.list([
          ...nodes.map((node) => {
            return python.TypeInstantiation.str(node.getNodeDisplayClassName());
          }),
        ]),
      });
      rootDisplayNodesInitFileStatements.push(nodeDisplayInitFileAllField);
    }

    const rootNodesInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? [
            ...this.workflowContext.parentNode.getNodeModulePath(),
            GENERATED_NODES_MODULE_NAME,
          ]
        : [this.workflowContext.moduleName, ...GENERATED_NODES_PATH],
      statements: rootNodesInitFileStatements,
    });

    const rootDisplayNodesInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? [
            ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
            GENERATED_NODES_MODULE_NAME,
          ]
        : [
            this.workflowContext.moduleName,
            ...GENERATED_DISPLAY_NODE_MODULE_PATH,
          ],
      statements: rootDisplayNodesInitFileStatements,
    });

    nodes.forEach((node) => {
      rootNodesInitFile.addReference(
        python.reference({
          name: node.getNodeClassName(),
          modulePath: node.getNodeModulePath(),
        })
      );

      rootDisplayNodesInitFile.addReference(
        python.reference({
          name: node.getNodeDisplayClassName(),
          modulePath: node.getNodeDisplayModulePath(),
        })
      );
    });

    const nodePromises = nodes.map(async (node) => {
      return await node.persist();
    });

    return [
      // nodes/__init__.py
      rootNodesInitFile.persist(),
      // display/nodes/__init__.py
      rootDisplayNodesInitFile.persist(),
      // nodes/* and display/nodes/*
      ...nodePromises,
    ];
  }

  private resolvePythonConfigFilePath(): string {
    if (
      process.env.ISORT_SETUP_CFG &&
      fs.existsSync(process.env.ISORT_SETUP_CFG)
    ) {
      return process.env.ISORT_SETUP_CFG;
    }

    const cwdPyProjectTomlPath = join(process.cwd(), "pyproject.toml");
    if (fs.existsSync(cwdPyProjectTomlPath)) {
      return cwdPyProjectTomlPath;
    }

    const parentDirPyProjectTomlPath = join(
      process.cwd(),
      "..",
      "pyproject.toml"
    );
    if (fs.existsSync(parentDirPyProjectTomlPath)) {
      return parentDirPyProjectTomlPath;
    }

    const rootDirPyProjectTomlPath = join(
      process.cwd(),
      "..",
      "..",
      "pyproject.toml"
    );
    if (fs.existsSync(rootDirPyProjectTomlPath)) {
      return rootDirPyProjectTomlPath;
    }

    const cwdSetupCfgPath = join(process.cwd(), "setup.cfg");
    if (fs.existsSync(cwdSetupCfgPath)) {
      return cwdSetupCfgPath;
    }

    const parentDirSetupCfgPath = join(process.cwd(), "..", "setup.cfg");
    if (fs.existsSync(parentDirSetupCfgPath)) {
      return parentDirSetupCfgPath;
    }

    const rootDirSetupCfgPath = join(process.cwd(), "..", "..", "setup.cfg");
    if (fs.existsSync(rootDirSetupCfgPath)) {
      return rootDirSetupCfgPath;
    }

    throw new Error("No isort Config file found");
  }
}
