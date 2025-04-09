import { mkdir } from "fs/promises";
import { join } from "path";

import { python } from "@fern-api/python-ast";
import { Comment } from "@fern-api/python-ast/Comment";
import { StarImport } from "@fern-api/python-ast/StarImport";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { VellumEnvironmentUrls } from "vellum-ai";

import * as codegen from "./codegen";
import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_DISPLAY_NODE_MODULE_PATH,
  GENERATED_NODES_MODULE_NAME,
  GENERATED_NODES_PATH,
} from "./constants";
import { createNodeContext, WorkflowContext } from "./context";
import { InputVariableContext } from "./context/input-variable-context";
import { WorkflowOutputContext } from "./context/workflow-output-context";
import { ErrorLogFile, InitFile, Inputs, Workflow } from "./generators";
import {
  NodeDefinitionGenerationError,
  ProjectSerializationError,
} from "./generators/errors";
import { BaseNode } from "./generators/nodes/bases";
import { GuardrailNode } from "./generators/nodes/guardrail-node";
import { InlineSubworkflowNode } from "./generators/nodes/inline-subworkflow-node";
import { SearchNode } from "./generators/nodes/search-node";
import { TemplatingNode } from "./generators/nodes/templating-node";

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
import { OutputVariableContext } from "src/context/output-variable-context";
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
import { WorkflowSandboxFile } from "src/generators/workflow-sandbox-file";
import { WorkflowVersionExecConfigSerializer } from "src/serializers/vellum";
import {
  FinalOutputNode as FinalOutputNodeType,
  WorkflowDataNode,
  WorkflowNodeType as WorkflowNodeTypeEnum,
  WorkflowSandboxInputs,
  WorkflowVersionExecConfig,
} from "src/types/vellum";
import { assertUnreachable, isNilOrEmpty } from "src/utils/typing";

export interface WorkflowProjectGeneratorOptions {
  /**
   * Used to override the default codegen behavior for Code Execution Nodes. If set to "STANDALONE",
   *  the node's code will be generated in a separate file. If set to "INLINE", the node's code will
   *  be inlined as a node attribute.
   */
  codeExecutionNodeCodeRepresentationOverride?: "STANDALONE" | "INLINE";
  disableFormatting?: boolean;
}

export declare namespace WorkflowProjectGenerator {
  interface BaseArgs {
    moduleName: string;
    strict?: boolean;
  }

  interface BaseProject extends BaseArgs {
    absolutePathToOutputDirectory: string;
    workflowsSdkModulePath?: readonly string[];
    workflowVersionExecConfigData: unknown;
    vellumApiKey?: string;
    vellumApiEnvironment?: VellumEnvironmentUrls;
    sandboxInputs?: WorkflowSandboxInputs[];
    options?: WorkflowProjectGeneratorOptions;
  }

  interface NestedProject extends BaseArgs {
    workflowContext: WorkflowContext;
    workflowVersionExecConfig: WorkflowVersionExecConfig;
  }

  type Args = BaseProject | NestedProject;
}

export class WorkflowProjectGenerator {
  public readonly workflowVersionExecConfig: WorkflowVersionExecConfig;
  public readonly workflowContext: WorkflowContext;
  private readonly sandboxInputs?: WorkflowSandboxInputs[];

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

      const workflowClassName =
        this.workflowVersionExecConfig.workflowRawData.definition?.name ||
        "Workflow";

      this.workflowContext = new WorkflowContext({
        workflowsSdkModulePath: rest.workflowsSdkModulePath,
        absolutePathToOutputDirectory: rest.absolutePathToOutputDirectory,
        moduleName,
        workflowClassName,
        vellumApiKey,
        vellumApiEnvironment: rest.vellumApiEnvironment,
        workflowRawData: this.workflowVersionExecConfig.workflowRawData,
        strict: rest.strict ?? false,
        disableFormatting: rest.options?.disableFormatting ?? false,
      });
      this.sandboxInputs = rest.sandboxInputs;
    }
  }

  public getModuleName(): string {
    return this.workflowContext.moduleName;
  }

  public async generateCode(): Promise<void> {
    const assets = await this.generateAssets().catch((error) => {
      this.workflowContext.addError(error);
      return null;
    });

    if (!assets) {
      return;
    }

    const { inputs, workflow, nodes } = assets;

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
      // sandbox.py
      ...(this.sandboxInputs ? [this.generateSandboxFile().persist()] : []),
    ]);

    // error.log - this gets generated separately from the other files because it
    // collects errors raised by the rest of the codegen process
    await this.generateErrorLogFile().persist();
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

    // TODO: Invert / remove this logic once output values are default and terminal nodes don't exist.
    // We are prioritizing terminal nodes as a temporary workaround to bad data from output values lingering in workflows.
    const terminalNodes =
      this.workflowVersionExecConfig.workflowRawData.nodes.filter(
        (nodeData): nodeData is FinalOutputNodeType =>
          nodeData.type === "TERMINAL"
      );

    if (terminalNodes.length > 0) {
      // Create from terminal nodes
      terminalNodes.forEach((nodeData) => {
        const outputVariableContext = new OutputVariableContext({
          outputVariableData: {
            id: nodeData.data.outputId,
            key: nodeData.data.name,
            type: nodeData.data.outputType,
          },
          workflowContext: this.workflowContext,
        });
        this.workflowContext.addOutputVariableContext(outputVariableContext);

        const workflowOutputContext = new WorkflowOutputContext({
          workflowContext: this.workflowContext,
          terminalNodeData: nodeData,
        });
        this.workflowContext.addWorkflowOutputContext(workflowOutputContext);
      });
    } else if (!isNilOrEmpty(this.workflowVersionExecConfig.outputVariables)) {
      const outputValuesById = Object.fromEntries(
        this.workflowVersionExecConfig.workflowRawData.outputValues?.map(
          (outputValue) => [outputValue.outputVariableId, outputValue]
        ) ?? []
      );
      this.workflowVersionExecConfig.outputVariables.forEach(
        (outputVariable) => {
          const outputVariableContext = new OutputVariableContext({
            outputVariableData: outputVariable,
            workflowContext: this.workflowContext,
          });
          this.workflowContext.addOutputVariableContext(outputVariableContext);

          const workflowOutput = outputValuesById[outputVariable.id];
          if (workflowOutput) {
            const workflowOutputContext = new WorkflowOutputContext({
              workflowContext: this.workflowContext,
              workflowOutputValue: workflowOutput,
            });
            this.workflowContext.addWorkflowOutputContext(
              workflowOutputContext
            );
          }
        }
      );
    }

    const nodesToGenerate = await Promise.all(
      this.getOrderedNodes().map(async (nodeData) => {
        await createNodeContext({
          workflowContext: this.workflowContext,
          nodeData,
        }).catch((error) => this.workflowContext.addError(error));
        return nodeData;
      })
    );

    const inputs = codegen.inputs({
      workflowContext: this.workflowContext,
    });

    const nodeIds = nodesToGenerate.map((nodeData) => nodeData.id);
    const nodes = await this.generateNodes(nodeIds);

    const workflow = codegen.workflow({
      moduleName,
      workflowContext: this.workflowContext,
      inputs,
      displayData: this.workflowVersionExecConfig.workflowRawData.displayData,
    });

    return { inputs, workflow, nodes };
  }

  /**
   * This method is used to order the nodes based on dependencies between them.
   * It ensures that nodes appear in the result after all the nodes they depend on.
   */
  private getOrderedNodes(): WorkflowDataNode[] {
    const rawData = this.workflowVersionExecConfig.workflowRawData;
    const nodes = rawData.nodes.filter(
      (node): node is WorkflowDataNode => node.type !== "ENTRYPOINT"
    );

    // Edge case: Workflow init only has two nodes of ENTRYPOINT and TERMINAL with no edge between them
    if (rawData.edges.length === 0) {
      return nodes;
    }

    const nodesById = Object.fromEntries(nodes.map((node) => [node.id, node]));

    // Create a dependency graph that represents the "depends on" relationships between nodes
    // If A depends on B, then B must come before A in the result
    const dependencyGraph: Map<string, Set<string>> = new Map();

    // Initialize dependency graph with all nodes
    nodes.forEach((node) => {
      dependencyGraph.set(node.id, new Set());
    });

    // Build dependency relationships based on edges
    rawData.edges.forEach((edge) => {
      const sourceNodeId = edge.sourceNodeId;
      const targetNodeId = edge.targetNodeId;

      const targetDependencies = dependencyGraph.get(targetNodeId);
      const sourceDependencies = dependencyGraph.get(sourceNodeId);
      if (targetDependencies && sourceDependencies) {
        targetDependencies.add(sourceNodeId);
      }
    });

    const orderedNodes: WorkflowDataNode[] = [];
    const visited = new Set<string>();
    const tempVisited = new Set<string>(); // Used to detect cycles

    // DFS function that ensures dependencies are processed first
    const visit = (nodeId: string) => {
      // Skip if already processed
      if (visited.has(nodeId)) {
        return;
      }

      // Return early if we've already visited this node in the current path (cycle)
      if (tempVisited.has(nodeId)) {
        return;
      }

      // Mark as temporarily visited (part of current path)
      tempVisited.add(nodeId);

      // Process all dependencies first
      const dependencies = dependencyGraph.get(nodeId) || new Set();
      for (const depId of dependencies) {
        visit(depId);
      }

      // All dependencies processed, now safe to add this node
      const node = nodesById[nodeId];
      if (node) {
        orderedNodes.push(node);
      }

      // Mark as fully processed
      visited.add(nodeId);
      tempVisited.delete(nodeId);
    };

    // Visit each node to ensure all are processed
    nodes.forEach((node) => {
      if (!visited.has(node.id)) {
        visit(node.id);
      }
    });

    return orderedNodes;
  }

  private async generateNodes(
    nodeIds: string[]
  ): Promise<BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[]> {
    const nodes: BaseNode<
      WorkflowDataNode,
      BaseNodeContext<WorkflowDataNode>
    >[] = [];

    await Promise.all(
      nodeIds.map(async (nodeId) => {
        let node: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>;

        const nodeContext = this.workflowContext.findNodeContext(nodeId);
        if (!nodeContext) {
          return;
        }

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
                throw new NodeDefinitionGenerationError(
                  `DEPLOYMENT variant not yet supported`
                );
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
                throw new NodeDefinitionGenerationError(
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
            throw new NodeDefinitionGenerationError(
              `Unsupported node type: ${nodeType}`
            );
          }
        }

        nodes.push(node);
      })
    );

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

  private generateErrorLogFile(): ErrorLogFile {
    return codegen.errorLogFile({
      workflowContext: this.workflowContext,
    });
  }

  private generateSandboxFile(): WorkflowSandboxFile {
    return codegen.workflowSandboxFile({
      workflowContext: this.workflowContext,
      sandboxInputs: this.sandboxInputs ?? [],
    });
  }

  /**
   * Gets the node file paths that have been tracked during code generation that will be merged by codegen-service
   * @returns Set of node file paths
   */
  public getPythonCodeMergeableNodeFiles(): Set<string> {
    return this.workflowContext.getPythonCodeMergeableNodeFiles();
  }
}
