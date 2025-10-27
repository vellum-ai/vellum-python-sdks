import child_process from "child_process";
import { mkdir, writeFile } from "fs/promises";
import * as path from "path";
import { join } from "path";

import { python } from "@fern-api/python-ast";
import { Comment } from "@fern-api/python-ast/Comment";
import { StarImport } from "@fern-api/python-ast/StarImport";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { VellumEnvironmentUrls } from "vellum-ai";

import * as codegen from "./codegen";
import { StateVariableContext } from "./context/state-variable-context";
import { getAllFilesInDir } from "./utils/files";

import {
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_NODES_MODULE_NAME,
} from "src/constants";
import { createNodeContext, WorkflowContext } from "src/context";
import { InputVariableContext } from "src/context/input-variable-context";
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
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { ErrorLogFile, InitFile, Inputs, Workflow } from "src/generators";
import {
  BaseCodegenError,
  NodeDefinitionGenerationError,
  ProjectSerializationError,
  WorkflowGenerationError,
} from "src/generators/errors";
import { ApiNode } from "src/generators/nodes/api-node";
import { BaseNode } from "src/generators/nodes/bases";
import { CodeExecutionNode } from "src/generators/nodes/code-execution-node";
import { ConditionalNode } from "src/generators/nodes/conditional-node";
import { ErrorNode } from "src/generators/nodes/error-node";
import { FinalOutputNode } from "src/generators/nodes/final-output-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import { GuardrailNode } from "src/generators/nodes/guardrail-node";
import { InlinePromptNode } from "src/generators/nodes/inline-prompt-node";
import { InlineSubworkflowNode } from "src/generators/nodes/inline-subworkflow-node";
import { MapNode } from "src/generators/nodes/map-node";
import { MergeNode } from "src/generators/nodes/merge-node";
import { NoteNode } from "src/generators/nodes/note-node";
import { PromptDeploymentNode } from "src/generators/nodes/prompt-deployment-node";
import { SearchNode } from "src/generators/nodes/search-node";
import { SubworkflowDeploymentNode } from "src/generators/nodes/subworkflow-deployment-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import { WorkflowSandboxFile } from "src/generators/workflow-sandbox-file";
import { WorkflowVersionExecConfigSerializer } from "src/serializers/vellum";
import {
  CodeResourceDefinition,
  FinalOutputNode as FinalOutputNodeType,
  WorkflowDataNode,
  WorkflowNodeType as WorkflowNodeTypeEnum,
  WorkflowSandboxDatasetRow,
  WorkflowVersionExecConfig,
} from "src/types/vellum";
import { getNodeLabel } from "src/utils/nodes";
import { isDefined, isNilOrEmpty } from "src/utils/typing";

export interface WorkflowProjectGeneratorOptions {
  /**
   * Used to override the default codegen behavior for Code Execution Nodes. If set to "STANDALONE",
   *  the node's code will be generated in a separate file. If set to "INLINE", the node's code will
   *  be inlined as a node attribute.
   */
  codeExecutionNodeCodeRepresentationOverride?: "STANDALONE" | "INLINE";
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
    sandboxInputs?: WorkflowSandboxDatasetRow[];
    skipInitFiles?: boolean;
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
  private readonly sandboxInputs?: WorkflowSandboxDatasetRow[];

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
        pythonCodeMergeableNodeFiles: new Set<string>(),
        triggers: this.workflowVersionExecConfig.triggers,
        skipInitFiles: rest.skipInitFiles,
      });
      this.sandboxInputs = rest.sandboxInputs;
    }
  }

  public getModuleName(): string {
    return this.workflowContext.moduleName;
  }

  public getModulePath(): string[] {
    return this.workflowContext.modulePath.slice(0, -1);
  }

  public async generateCode(
    originalArtifact?: Record<string, string>
  ): Promise<void> {
    const absolutePathToModuleDirectory = join(
      this.workflowContext.absolutePathToOutputDirectory,
      ...this.getModulePath()
    );

    await mkdir(absolutePathToModuleDirectory, {
      recursive: true,
    });

    const assets = await this.generateAssets().catch((error) => {
      if (error instanceof BaseCodegenError) {
        this.workflowContext.addError(error);
      } else {
        console.error("Unexpected error generating assets", error);
        this.workflowContext.addError(
          new WorkflowGenerationError(
            `Failed to generate assets for workflow ${this.workflowContext.workflowClassName}.`,
            "WARNING"
          )
        );
      }
      return null;
    });

    if (!assets) {
      return;
    }

    const { inputs, workflow, nodes } = assets;

    const state = codegen.state({
      workflowContext: this.workflowContext,
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
      // state.py
      state.persist(),
      // workflow.py
      workflow.getWorkflowFile().persist(),
      // nodes/*
      ...this.generateNodeFiles(nodes),
      // sandbox.py
      ...(this.sandboxInputs ? [this.generateSandboxFile().persist()] : []),
      this.writeAdditionalFiles(),
    ]);

    // Code merge logic - copied from codegen-service
    if (originalArtifact) {
      await this.mergeFilesWithArtifact(originalArtifact);
    }

    // error.log - this gets generated separately from the other files because it
    // collects errors raised by the rest of the codegen process
    await this.generateErrorLogFile().persist();
  }

  private runProcess = <INPUT, OUTPUT>({
    inputData,
    command,
    args,
  }: {
    inputData: INPUT;
    command: string;
    args: string[];
  }): Promise<OUTPUT> => {
    return new Promise((resolve, reject) => {
      try {
        let errorOutput = "";
        let output = "";

        const proc = child_process.spawn(command, args, {
          stdio: ["pipe", "pipe", "pipe"],
          env: {
            PYTHONPATH: ".",
            PATH: process.env.PATH,
          },
        });

        const timer = setTimeout(() => {
          if (proc.exitCode === null) {
            proc.kill();
          }
        }, 120 * 1000);

        proc.stdout.on("data", (data) => {
          output += data.toString();
        });

        proc.on("error", (err) => {
          reject(`Process failed to start: ${err}`);
        });

        proc.stderr.on("data", (data) => {
          errorOutput += data.toString();
        });

        proc.on("exit", (code) => {
          try {
            clearTimeout(timer);

            if (code !== 0) {
              reject(
                `Error merging code, exit code ${code} output:\n ${errorOutput} ${output}`
              );
            } else {
              resolve(JSON.parse(output));
            }
          } catch (e) {
            reject(e);
          }
        });

        if (proc.exitCode === null) {
          proc.stdin.write(
            JSON.stringify(inputData) + "\n--vellum-input-stop--\n"
          );
          proc.stdin.end();
        }
      } catch (e) {
        reject(e);
      }
    });
  };

  private async mergeFilesWithArtifact(
    originalArtifact: Record<string, string>
  ): Promise<void> {
    const pythonCodeMergeableNodeFiles = this.getPythonCodeMergeableNodeFiles();

    const shouldEnableCodeMerge = pythonCodeMergeableNodeFiles.size > 0;

    if (!shouldEnableCodeMerge) {
      return;
    }

    const filteredOriginalFileMap = Object.fromEntries(
      Object.entries(originalArtifact).filter(([filePath]) =>
        pythonCodeMergeableNodeFiles.has(filePath)
      )
    );

    const absolutePathToModuleDirectory = join(
      this.workflowContext.absolutePathToOutputDirectory,
      ...this.getModulePath()
    );

    const generatedFiles = await getAllFilesInDir(
      absolutePathToModuleDirectory
    );

    try {
      const codeMergeResult = await this.runProcess({
        inputData: {
          originalFileMap: filteredOriginalFileMap,
          generatedFileMap: generatedFiles,
        },
        command:
          process.env.NODE_ENV === "production"
            ? "python"
            : path.join(__dirname, "../../../.venv/bin/python"),
        args: ["python_file_merging/merge_cli.py"],
      });

      if (typeof codeMergeResult !== "object") {
        throw new Error(
          `Code merge result returned an invalid response: ${codeMergeResult}`
        );
      }

      await this.persistMergedFiles(
        codeMergeResult as Record<string, string>,
        absolutePathToModuleDirectory
      );
    } catch (error) {
      console.error("Code merge failed:", error);
    }
  }

  private async persistMergedFiles(
    mergedFiles: Record<string, string>,
    baseDirectory: string
  ): Promise<void> {
    const writePromises = Object.entries(mergedFiles).map(
      async ([filePath, content]) => {
        const fullPath = join(baseDirectory, filePath);
        await mkdir(path.dirname(fullPath), { recursive: true });
        await writeFile(fullPath, content);
      }
    );

    await Promise.all(writePromises);
  }

  private generateRootInitFile(): InitFile {
    const statements: AstNode[] = [];
    const imports: StarImport[] = [];
    const comments: Comment[] = [];

    const parentNode = this.workflowContext.parentNode;
    if (parentNode) {
      if (this.workflowContext.nestedWorkflowModuleName) {
        comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
        const parentDisplayModulePath = parentNode.getNodeDisplayModulePath();
        const displayIndex = parentDisplayModulePath.indexOf(
          GENERATED_DISPLAY_MODULE_NAME
        );
        const sliceEnd = displayIndex !== -1 ? displayIndex + 1 : 1;

        imports.push(
          python.starImport({
            modulePath: parentDisplayModulePath.slice(0, sliceEnd),
          })
        );
      } else {
        statements.push(parentNode.generateNodeClass());
      }
    } else {
      comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      imports.push(
        python.starImport({
          modulePath: [...this.getModulePath(), GENERATED_DISPLAY_MODULE_NAME],
        })
      );
    }

    const rootInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.getModulePath(),
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
      if (this.workflowContext.nestedWorkflowModuleName) {
        imports.push(
          python.starImport({
            modulePath: [".nodes"],
          })
        );

        imports.push(
          python.starImport({
            modulePath: [".workflow"],
          })
        );
        comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      } else {
        const parentModulePath = [...parentNode.getNodeDisplayModulePath()];
        imports.push(
          python.starImport({
            modulePath: [...parentModulePath, "nodes"],
          })
        );
        imports.push(
          python.starImport({
            modulePath: [...parentModulePath, "workflow"],
          })
        );
        statements.push(...parentNode.generateNodeDisplayClasses());
        comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      }
    } else {
      comments.push(python.comment({ docs: "flake8: noqa: F401, F403" }));
      imports.push(
        python.starImport({
          modulePath: [
            ...this.getModulePath(),
            GENERATED_DISPLAY_MODULE_NAME,
            "nodes",
          ],
        })
      );
      imports.push(
        python.starImport({
          modulePath: [
            ...this.getModulePath(),
            GENERATED_DISPLAY_MODULE_NAME,
            "workflow",
          ],
        })
      );
    }

    const rootDisplayInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? this.workflowContext.nestedWorkflowModuleName
          ? [
              ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
              this.workflowContext.nestedWorkflowModuleName,
            ]
          : this.workflowContext.parentNode.getNodeDisplayModulePath()
        : [...this.getModulePath(), GENERATED_DISPLAY_MODULE_NAME],
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
    this.workflowVersionExecConfig.inputVariables.forEach((inputVariable) => {
      const inputVariableContext = new InputVariableContext({
        inputVariableData: inputVariable,
        workflowContext: this.workflowContext,
      });
      this.workflowContext.addInputVariableContext(inputVariableContext);
    });

    if (this.workflowVersionExecConfig.stateVariables) {
      this.workflowVersionExecConfig.stateVariables.forEach((stateVariable) => {
        const stateVariableContext = new StateVariableContext({
          stateVariableData: stateVariable,
          workflowContext: this.workflowContext,
        });
        this.workflowContext.addStateVariableContext(stateVariableContext);
      });
    }

    const registeredWorkflowOutputNodeIds = new Set<string>();
    const registeredOutputVariableIds = new Set<string>();
    const registeredOutputVariableNames = new Set<string>();
    if (!isNilOrEmpty(this.workflowVersionExecConfig.outputVariables)) {
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
          registeredOutputVariableNames.add(outputVariable.key);
          registeredOutputVariableIds.add(outputVariable.id);
          if (workflowOutput) {
            const workflowOutputContext = new WorkflowOutputContext({
              workflowContext: this.workflowContext,
              workflowOutputValue: workflowOutput,
            });
            this.workflowContext.addWorkflowOutputContext(
              workflowOutputContext
            );
            if (workflowOutput.value?.type === "NODE_OUTPUT") {
              registeredWorkflowOutputNodeIds.add(workflowOutput.value.nodeId);
            }
          }
        }
      );
    }

    // Create from terminal nodes that aren't already in the output variables
    const terminalNodes =
      this.workflowVersionExecConfig.workflowRawData.nodes.filter(
        (nodeData): nodeData is FinalOutputNodeType =>
          nodeData.type === "TERMINAL"
      );
    terminalNodes.forEach((nodeData) => {
      if (
        !registeredOutputVariableIds.has(nodeData.data.outputId) &&
        !registeredOutputVariableNames.has(nodeData.data.name)
      ) {
        const outputVariableContext = new OutputVariableContext({
          outputVariableData: {
            id: nodeData.data.outputId,
            key: nodeData.data.name,
            type: nodeData.data.outputType,
          },
          workflowContext: this.workflowContext,
        });
        this.workflowContext.addOutputVariableContext(outputVariableContext);
      }

      if (registeredWorkflowOutputNodeIds.has(nodeData.id)) {
        return;
      }
      const workflowOutputContext = new WorkflowOutputContext({
        workflowContext: this.workflowContext,
        terminalNodeData: nodeData,
      });
      this.workflowContext.addWorkflowOutputContext(workflowOutputContext);
    });

    const nodesToGenerate = await Promise.all(
      this.getOrderedNodes().map(async (nodeData) => {
        try {
          await createNodeContext({
            workflowContext: this.workflowContext,
            nodeData,
          });
          return nodeData.id;
        } catch (error) {
          if (error instanceof BaseCodegenError) {
            this.workflowContext.addError(error);
          } else {
            console.error("Unexpected error creating node context", error);
            const nodeLabel = getNodeLabel(nodeData);
            this.workflowContext.addError(
              new NodeDefinitionGenerationError(
                `Failed to create node context for node ${nodeLabel}.`,
                "WARNING"
              )
            );
          }
          return null;
        }
      })
    );

    const inputs = codegen.inputs({
      workflowContext: this.workflowContext,
    });

    const nodeIds = nodesToGenerate.filter(
      (nodeId): nodeId is string => nodeId !== null
    );
    const nodes = this.generateNodes(nodeIds);

    const workflow = codegen.workflow({
      workflowContext: this.workflowContext,
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
    // Process source node before target node
    rawData.edges.forEach((edge) => {
      dependencyGraph.get(edge.targetNodeId)?.add(edge.sourceNodeId);
    });

    const orderedNodes: WorkflowDataNode[] = [];
    const visited = new Set<string>();
    const tempVisited = new Set<string>(); // Used to detect cycles

    const processNode = (nodeId: string) => {
      const node = nodesById[nodeId];
      if (node && !visited.has(nodeId)) {
        orderedNodes.push(node);
      }

      // Mark as fully processed
      visited.add(nodeId);
      tempVisited.delete(nodeId);
    };

    // DFS function that ensures dependencies are processed first
    const visit = (nodeId: string) => {
      // Skip if already processed
      if (visited.has(nodeId)) {
        return;
      }

      // Return early if we've already visited this node in the current path (cycle)
      // Make sure we add the node that started the cycle first
      if (tempVisited.has(nodeId)) {
        processNode(nodeId);
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
      processNode(nodeId);
    };

    // Visit each node to ensure all are processed
    nodes.forEach((node) => {
      if (!visited.has(node.id)) {
        visit(node.id);
      }
    });

    return orderedNodes;
  }

  private generateNodes(
    nodeIds: string[]
  ): BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[] {
    return nodeIds
      .map((nodeId) => {
        const nodeContext = this.workflowContext.findNodeContext(nodeId);
        if (!nodeContext) {
          return;
        }
        return nodeContext;
      })
      .filter(isDefined)
      .map((nodeContext) => {
        const nodeData = nodeContext.nodeData;

        const nodeType = nodeData.type;
        switch (nodeType) {
          case WorkflowNodeTypeEnum.SEARCH: {
            return new SearchNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as TextSearchNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.SUBWORKFLOW: {
            const variant = nodeData.data.variant;
            switch (variant) {
              case "INLINE":
                return new InlineSubworkflowNode({
                  workflowContext: this.workflowContext,
                  nodeContext: nodeContext as InlineSubworkflowNodeContext,
                });
              case "DEPLOYMENT":
                return new SubworkflowDeploymentNode({
                  workflowContext: this.workflowContext,
                  nodeContext: nodeContext as SubworkflowDeploymentNodeContext,
                });
              default: {
                throw new NodeDefinitionGenerationError(
                  `Unsupported Subworkflow Node variant: ${variant}`
                );
              }
            }
          }
          case WorkflowNodeTypeEnum.MAP: {
            const mapNodeVariant = nodeData.data.variant;
            switch (mapNodeVariant) {
              case "INLINE":
                return new MapNode({
                  workflowContext: this.workflowContext,
                  nodeContext: nodeContext as MapNodeContext,
                });
              case "DEPLOYMENT":
                throw new NodeDefinitionGenerationError(
                  `DEPLOYMENT variant not yet supported`
                );
              default: {
                throw new NodeDefinitionGenerationError(
                  `Unsupported Map Node variant: ${mapNodeVariant}`
                );
              }
            }
          }
          case WorkflowNodeTypeEnum.METRIC: {
            return new GuardrailNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as GuardrailNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.CODE_EXECUTION: {
            return new CodeExecutionNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as CodeExecutionContext,
            });
          }
          case WorkflowNodeTypeEnum.PROMPT: {
            const promptNodeVariant = nodeData.data.variant;

            switch (promptNodeVariant) {
              case "INLINE":
                return new InlinePromptNode({
                  workflowContext: this.workflowContext,
                  nodeContext: nodeContext as InlinePromptNodeContext,
                });
              case "DEPLOYMENT":
                return new PromptDeploymentNode({
                  workflowContext: this.workflowContext,
                  nodeContext: nodeContext as PromptDeploymentNodeContext,
                });
              case "LEGACY":
                throw new NodeDefinitionGenerationError(
                  `LEGACY variant should have been converted to INLINE variant by this point.`
                );
              default: {
                throw new NodeDefinitionGenerationError(
                  `Unsupported Prompt Node variant: ${promptNodeVariant}`
                );
              }
            }
          }
          case WorkflowNodeTypeEnum.TEMPLATING: {
            return new TemplatingNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as TemplatingNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.CONDITIONAL: {
            return new ConditionalNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as ConditionalNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.TERMINAL: {
            return new FinalOutputNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as FinalOutputNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.MERGE: {
            return new MergeNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as MergeNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.ERROR: {
            return new ErrorNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as ErrorNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.NOTE: {
            return new NoteNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as NoteNodeContext,
            });
          }
          case WorkflowNodeTypeEnum.API:
            return new ApiNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as ApiNodeContext,
            });
          case WorkflowNodeTypeEnum.GENERIC:
            return new GenericNode({
              workflowContext: this.workflowContext,
              nodeContext: nodeContext as GenericNodeContext,
            });
          default: {
            throw new NodeDefinitionGenerationError(
              `Unsupported node type: ${nodeType}`
            );
          }
        }
      });
  }

  private sortAlphabetically(items: string[]): string[] {
    return items.sort((a, b) => a.localeCompare(b));
  }

  private generateNodeFiles(
    nodes: BaseNode<WorkflowDataNode, BaseNodeContext<WorkflowDataNode>>[]
  ): Promise<unknown>[] {
    const rootNodesInitFileStatements: AstNode[] = [];
    const rootDisplayNodesInitFileStatements: AstNode[] = [];
    if (nodes.length) {
      const nodeInitFileAllField = python.field({
        name: "__all__",
        initializer: python.TypeInstantiation.list(
          [
            ...this.sortAlphabetically(
              nodes.map((node) => node.getNodeClassName())
            ).map((name) => python.TypeInstantiation.str(name)),
          ],
          {
            endWithComma: true,
          }
        ),
      });
      rootNodesInitFileStatements.push(nodeInitFileAllField);

      const nodeDisplayInitFileAllField = python.field({
        name: "__all__",
        initializer: python.TypeInstantiation.list(
          [
            ...this.sortAlphabetically(
              nodes.map((node) => node.getNodeDisplayClassName())
            ).map((name) => python.TypeInstantiation.str(name)),
          ],
          {
            endWithComma: true,
          }
        ),
      });
      rootDisplayNodesInitFileStatements.push(nodeDisplayInitFileAllField);
    }

    const rootNodesInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? this.workflowContext.nestedWorkflowModuleName
          ? [
              ...this.workflowContext.parentNode.nodeContext.nodeModulePath,
              this.workflowContext.nestedWorkflowModuleName,
              GENERATED_NODES_MODULE_NAME,
            ]
          : [
              ...this.workflowContext.parentNode.nodeContext.nodeModulePath,
              GENERATED_NODES_MODULE_NAME,
            ]
        : [...this.getModulePath(), GENERATED_NODES_MODULE_NAME],
      statements: rootNodesInitFileStatements,
    });

    const rootDisplayNodesInitFile = codegen.initFile({
      workflowContext: this.workflowContext,
      modulePath: this.workflowContext.parentNode
        ? this.workflowContext.nestedWorkflowModuleName
          ? [
              ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
              this.workflowContext.nestedWorkflowModuleName,
              GENERATED_NODES_MODULE_NAME,
            ]
          : [
              ...this.workflowContext.parentNode.getNodeDisplayModulePath(),
              GENERATED_NODES_MODULE_NAME,
            ]
        : [
            ...this.getModulePath(),
            GENERATED_DISPLAY_MODULE_NAME,
            GENERATED_NODES_MODULE_NAME,
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

    if (this.workflowContext.skipInitFiles) {
      return [...nodePromises];
    }

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
  private async writeAdditionalFiles(): Promise<void> {
    const moduleData = this.workflowVersionExecConfig.moduleData;
    if (!moduleData?.additionalFiles) {
      return;
    }

    const absolutePathToModuleDirectory = join(
      this.workflowContext.absolutePathToOutputDirectory,
      ...this.getModulePath()
    );

    await Promise.all(
      Object.entries(moduleData.additionalFiles).map(
        async ([relativePath, content]) => {
          const fullPath = join(absolutePathToModuleDirectory, relativePath);
          await mkdir(path.dirname(fullPath), { recursive: true });
          await writeFile(fullPath, content);
        }
      )
    );
  }

  public getPythonCodeMergeableNodeFiles(): Set<string> {
    return this.workflowContext.getPythonCodeMergeableNodeFiles();
  }

  public getNodeIdToFileMapping(): Record<string, CodeResourceDefinition> {
    return Object.fromEntries(
      Array.from(this.workflowContext.globalNodeContextsByNodeId.entries()).map(
        ([nodeId, nodeContext]) => [
          nodeId,
          nodeContext.nodeData.definition ?? {
            name: nodeContext.nodeClassName,
            module: nodeContext.nodeModulePath,
          },
        ]
      )
    );
  }
}
