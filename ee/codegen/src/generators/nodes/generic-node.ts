import { mkdir, writeFile } from "fs/promises";
import { join } from "path";

import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import {
  PromptBlock as PromptBlockSerializer,
  PromptParameters as PromptParametersSerializer,
} from "vellum-ai/serialization";

import {
  GENERATED_WORKFLOW_MODULE_NAME,
  OUTPUTS_CLASS_NAME,
  VELLUM_WORKFLOW_DEFINITION_PATH,
} from "src/constants";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { PromptBlock as PromptBlockType } from "src/generators/base-prompt-block";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { InitFile } from "src/generators/init-file";
import { NodeOutputs } from "src/generators/node-outputs";
import { BaseNode } from "src/generators/nodes/bases/base";
import { AttributeType, NODE_ATTRIBUTES } from "src/generators/nodes/constants";
import { PromptBlock } from "src/generators/prompt-block";
import { PromptParameters } from "src/generators/prompt-parameters-request";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { WorkflowProjectGenerator } from "src/project";
import { WorkflowVersionExecConfigSerializer } from "src/serializers/vellum";
import {
  ComposioToolFunctionArgs,
  FunctionArgs,
  GenericNode as GenericNodeType,
  InlineWorkflowFunctionArgs,
  MCPServerFunctionArgs,
  WorkflowDeploymentFunctionArgs,
  WorkflowRawData,
  WorkflowVersionExecConfig,
} from "src/types/vellum";
import {
  createPythonClassName,
  toPythonSafeSnakeCase,
  toValidPythonIdentifier,
} from "src/utils/casing";

export class GenericNode extends BaseNode<GenericNodeType, GenericNodeContext> {
  private functionsToGenerate: Array<{
    functionName: string;
    content: string;
  }> = [];

  private inlineWorkflowsToGenerate: Array<{
    functionName: string;
    workflowProject: WorkflowProjectGenerator;
  }> = [];

  private nodeAttributes: AstNode[] = [];

  // True for node that has additional assets generated from attributes like functions or subworkflows
  private isNestedNode: boolean = false;

  constructor(args: BaseNode.Args<GenericNodeType, GenericNodeContext>) {
    super(args);

    this.nodeAttributes = this.generateNodeAttributes();
  }

  private generateNodeAttributes(): AstNode[] {
    const nodeAttributes = NODE_ATTRIBUTES[this.nodeData.base.name] ?? {};

    const nodeAttributesStatements: AstNode[] = [];

    this.nodeData.attributes.forEach((attribute) => {
      const attributeConfig = nodeAttributes[attribute.name];
      switch (attributeConfig?.type) {
        case AttributeType.Functions: {
          this.isNestedNode = true;
          const value = attribute.value;

          if (
            value?.type === "CONSTANT_VALUE" &&
            value.value?.type === "JSON" &&
            Array.isArray(value.value.value)
          ) {
            const functions: Array<
              | FunctionArgs
              | InlineWorkflowFunctionArgs
              | WorkflowDeploymentFunctionArgs
              | ComposioToolFunctionArgs
              | MCPServerFunctionArgs
            > = value.value.value;

            const codeExecutionFunctions: FunctionArgs[] = [];
            const inlineWorkflowFunctions: InlineWorkflowFunctionArgs[] = [];
            const deploymentWorkflowFunctions: WorkflowDeploymentFunctionArgs[] =
              [];
            const functionReferences: python.AstNode[] = [];

            functions.forEach((f) => {
              switch (f.type) {
                case "CODE_EXECUTION": {
                  codeExecutionFunctions.push(f as FunctionArgs);
                  if (f.name) {
                    const snakeName = toPythonSafeSnakeCase(f.name);
                    // Use toValidPythonIdentifier to ensure the name is safe for Python references
                    // but preserve original casing when possible (see APO-1372)
                    const safeName = toValidPythonIdentifier(f.name);
                    functionReferences.push(
                      python.reference({
                        name: safeName, // Use safe Python identifier that preserves original casing
                        modulePath: [`.${snakeName}`], // Import from snake_case module
                      })
                    );
                  }
                  break;
                }
                case "INLINE_WORKFLOW": {
                  const rawExecConfig =
                    f.exec_config as unknown as WorkflowVersionExecConfigSerializer.Raw;
                  const workflowVersionExecConfigResult =
                    WorkflowVersionExecConfigSerializer.parse(rawExecConfig, {
                      allowUnrecognizedUnionMembers: true,
                      allowUnrecognizedEnumValues: true,
                      unrecognizedObjectKeys: "strip",
                    });
                  if (!workflowVersionExecConfigResult.ok) {
                    this.workflowContext.addError(
                      new NodeDefinitionGenerationError(
                        `Failed to parse WorkflowVersionExecConfig: ${JSON.stringify(
                          workflowVersionExecConfigResult.errors
                        )}`,
                        "WARNING"
                      )
                    );
                  } else {
                    const workflowVersionExecConfig: WorkflowVersionExecConfig =
                      workflowVersionExecConfigResult.value;
                    const workflow: InlineWorkflowFunctionArgs = {
                      type: "INLINE_WORKFLOW",
                      name: f.name,
                      description: f.description,
                      exec_config: workflowVersionExecConfig,
                    };
                    inlineWorkflowFunctions.push(workflow);

                    const workflowName =
                      this.getInlineWorkflowFunctionName(workflow);
                    if (workflowName) {
                      const nestedProject =
                        this.getNestedWorkflowProject(workflow);
                      const workflowClassName =
                        nestedProject.workflowContext.workflowClassName;
                      functionReferences.push(
                        python.reference({
                          name: workflowClassName,
                          modulePath: [
                            `.${workflowName}`,
                            GENERATED_WORKFLOW_MODULE_NAME,
                          ],
                        })
                      );
                    }
                  }
                  break;
                }
                case "WORKFLOW_DEPLOYMENT": {
                  const workflowDeployment: WorkflowDeploymentFunctionArgs = {
                    type: "WORKFLOW_DEPLOYMENT",
                    name: f.name,
                    description: f.description,
                    deployment: f.deployment,
                    release_tag: f.release_tag,
                  };
                  deploymentWorkflowFunctions.push(workflowDeployment);
                  const workflowDeploymentName = workflowDeployment.deployment;
                  const args = [
                    python.methodArgument({
                      name: "deployment",
                      value: python.TypeInstantiation.str(
                        workflowDeploymentName
                      ),
                    }),
                  ];

                  if (f.release_tag !== null) {
                    args.push(
                      python.methodArgument({
                        name: "release_tag",
                        value: python.TypeInstantiation.str(f.release_tag),
                      })
                    );
                  }

                  functionReferences.push(
                    python.instantiateClass({
                      classReference: python.reference({
                        name: "DeploymentDefinition",
                        modulePath: [
                          "vellum",
                          "workflows",
                          "types",
                          "definition",
                        ],
                      }),
                      arguments_: args,
                    })
                  );
                  break;
                }
                case "COMPOSIO": {
                  const composioTool = f as ComposioToolFunctionArgs;

                  // Validate required fields and provide fallbacks for missing fields
                  // Frontend sends integration_name and tool_slug, but backend sends toolkit and action
                  const toolkit =
                    composioTool.integration_name ||
                    composioTool.toolkit ||
                    "UNKNOWN";
                  const action =
                    composioTool.tool_slug || composioTool.action || "UNKNOWN";
                  const description = composioTool.description || "UNKNOWN";

                  const args = [
                    python.methodArgument({
                      name: "toolkit",
                      value: python.TypeInstantiation.str(toolkit),
                    }),
                    python.methodArgument({
                      name: "action",
                      value: python.TypeInstantiation.str(action),
                    }),
                    python.methodArgument({
                      name: "description",
                      value: python.TypeInstantiation.str(description),
                    }),
                  ];

                  if (composioTool.user_id != null) {
                    args.push(
                      python.methodArgument({
                        name: "user_id",
                        value: python.TypeInstantiation.str(
                          composioTool.user_id
                        ),
                      })
                    );
                  }

                  functionReferences.push(
                    python.instantiateClass({
                      classReference: python.reference({
                        name: "ComposioToolDefinition",
                        modulePath: VELLUM_WORKFLOW_DEFINITION_PATH,
                      }),
                      arguments_: args,
                    })
                  );
                  break;
                }
                case "MCP_SERVER": {
                  const mcpServerFunction = f as MCPServerFunctionArgs;

                  const arguments_: python.MethodArgument[] = [
                    python.methodArgument({
                      name: "name",
                      value: python.TypeInstantiation.str(
                        mcpServerFunction.name
                      ),
                    }),
                    python.methodArgument({
                      name: "url",
                      value: python.TypeInstantiation.str(
                        mcpServerFunction.url
                      ),
                    }),
                  ];

                  if (mcpServerFunction.authorization_type) {
                    arguments_.push(
                      python.methodArgument({
                        name: "authorization_type",
                        value: python.reference({
                          name: "AuthorizationType",
                          modulePath: [
                            ...this.workflowContext.sdkModulePathNames
                              .WORKFLOWS_MODULE_PATH,
                            "constants",
                          ],
                          attribute: [mcpServerFunction.authorization_type],
                        }),
                      })
                    );
                  }

                  if (
                    mcpServerFunction.authorization_type === "BEARER_TOKEN" &&
                    mcpServerFunction.bearer_token_value
                  ) {
                    arguments_.push(
                      python.methodArgument({
                        name: "bearer_token_value",
                        value: new WorkflowValueDescriptor({
                          workflowValueDescriptor: {
                            type: "ENVIRONMENT_VARIABLE",
                            environmentVariable:
                              mcpServerFunction.bearer_token_value,
                          },
                          nodeContext: this.nodeContext,
                          workflowContext: this.workflowContext,
                        }),
                      })
                    );
                  }

                  if (
                    mcpServerFunction.authorization_type === "API_KEY" &&
                    mcpServerFunction.api_key_header_key
                  ) {
                    arguments_.push(
                      python.methodArgument({
                        name: "api_key_header_key",
                        value: python.TypeInstantiation.str(
                          mcpServerFunction.api_key_header_key
                        ),
                      })
                    );
                  }

                  if (
                    mcpServerFunction.authorization_type === "API_KEY" &&
                    mcpServerFunction.api_key_header_value
                  ) {
                    arguments_.push(
                      python.methodArgument({
                        name: "api_key_header_value",
                        value: new WorkflowValueDescriptor({
                          workflowValueDescriptor: {
                            type: "ENVIRONMENT_VARIABLE",
                            environmentVariable:
                              mcpServerFunction.api_key_header_value,
                          },
                          nodeContext: this.nodeContext,
                          workflowContext: this.workflowContext,
                        }),
                      })
                    );
                  }

                  functionReferences.push(
                    python.instantiateClass({
                      classReference: python.reference({
                        name: "MCPServer",
                        modulePath: VELLUM_WORKFLOW_DEFINITION_PATH,
                      }),
                      arguments_,
                    })
                  );
                  break;
                }

                default:
                  this.workflowContext.addError(
                    new NodeDefinitionGenerationError(
                      `Unsupported function type: ${JSON.stringify(
                        f
                      )}. Only CODE_EXECUTION, INLINE_WORKFLOW, WORKFLOW_DEPLOYMENT, and COMPOSIO are supported.`,
                      "WARNING"
                    )
                  );
              }
            });

            if (codeExecutionFunctions.length > 0) {
              this.generateFunctionFile(codeExecutionFunctions);
            }

            if (inlineWorkflowFunctions.length > 0) {
              this.generateInlineWorkflowFiles(inlineWorkflowFunctions);
            }

            nodeAttributesStatements.push(
              python.field({
                name: attribute.name,
                initializer: python.TypeInstantiation.list(functionReferences),
              })
            );
          }
          break;
        }
        case AttributeType.PromptBlocks: {
          const blocks = attribute.value;

          if (
            blocks &&
            blocks.type === "CONSTANT_VALUE" &&
            blocks.value?.type === "JSON"
          ) {
            const rawBlocks = blocks.value.value as PromptBlockSerializer.Raw[];
            const deserializedBlocks: PromptBlockType[] = [];

            rawBlocks.forEach((block, index) => {
              const parseResult = PromptBlockSerializer.parse(block, {
                unrecognizedObjectKeys: "strip",
              });
              if (parseResult.ok) {
                // TODO: Remove `as` once other types of blocks are supported
                deserializedBlocks.push(parseResult.value as PromptBlockType);
              } else {
                this.workflowContext.addError(
                  new NodeDefinitionGenerationError(
                    `Failed to parse block at index ${index}: ${JSON.stringify(
                      parseResult.errors
                    )}`,
                    "WARNING"
                  )
                );
              }
            });

            // Build the mapping from input variable ID to key from prompt_inputs attribute
            const inputVariableNameById: Record<string, string> = {};
            const promptInputsAttr = this.nodeData.attributes.find(
              (attr) => attr.name === "prompt_inputs"
            );
            if (
              promptInputsAttr &&
              promptInputsAttr.value?.type === "DICTIONARY_REFERENCE" &&
              promptInputsAttr.value.entries
            ) {
              for (const entry of promptInputsAttr.value.entries) {
                if (entry.id && entry.key) {
                  inputVariableNameById[entry.id] = entry.key;
                }
              }
            }

            nodeAttributesStatements.push(
              python.field({
                name: attribute.name,
                initializer: python.TypeInstantiation.list(
                  deserializedBlocks.map((block) => {
                    return new PromptBlock({
                      workflowContext: this.workflowContext,
                      promptBlock: block,
                      inputVariableNameById: inputVariableNameById,
                    });
                  }),
                  {
                    endWithComma: true,
                  }
                ),
              })
            );
          }
          break;
        }
        case AttributeType.Parameters: {
          if (
            attribute.value &&
            attribute.value.type === "CONSTANT_VALUE" &&
            attribute.value.value?.type === "JSON"
          ) {
            const parseResult = PromptParametersSerializer.parse(
              attribute.value.value.value
            );
            if (!parseResult.ok) {
              this.workflowContext.addError(
                new NodeDefinitionGenerationError(
                  `Failed to parse parameters attribute: ${JSON.stringify(
                    parseResult.errors
                  )}`,
                  "WARNING"
                )
              );
              break;
            }
            const promptParameters = parseResult.value;
            nodeAttributesStatements.push(
              python.field({
                name: "parameters",
                initializer: new PromptParameters({
                  promptParametersRequest: promptParameters,
                }),
              })
            );
          }
          break;
        }
        default:
          nodeAttributesStatements.push(
            python.field({
              name: toPythonSafeSnakeCase(attribute.name),
              initializer: new WorkflowValueDescriptor({
                nodeContext: this.nodeContext,
                workflowValueDescriptor: attribute.value,
                workflowContext: this.workflowContext,
              }),
            })
          );
      }
    });

    return nodeAttributesStatements;
  }

  getInnerWorkflowData(workflow: InlineWorkflowFunctionArgs): WorkflowRawData {
    return workflow.exec_config.workflowRawData;
  }

  private getNestedWorkflowProject(
    workflow: InlineWorkflowFunctionArgs
  ): WorkflowProjectGenerator {
    const workflowName = this.getInlineWorkflowFunctionName(workflow);

    const nestedWorkflowLabel = workflowName;
    const nestedWorkflowClassName = createPythonClassName(nestedWorkflowLabel);
    const nestedWorkflowContext =
      this.workflowContext.createNestedWorkflowContext({
        parentNode: this,
        workflowClassName: nestedWorkflowClassName,
        workflowClassDescription: workflow.description,
        workflowRawData: workflow.exec_config.workflowRawData,
        classNames: this.workflowContext.classNames,
        nestedWorkflowModuleName: workflowName,
      });

    return new WorkflowProjectGenerator({
      workflowVersionExecConfig: {
        workflowRawData: workflow.exec_config.workflowRawData,
        inputVariables: workflow.exec_config.inputVariables,
        stateVariables: [],
        outputVariables: workflow.exec_config.outputVariables,
      },
      moduleName: nestedWorkflowContext.moduleName,
      workflowContext: nestedWorkflowContext,
    });
  }

  private getInlineWorkflowFunctionName(
    workflow: InlineWorkflowFunctionArgs
  ): string {
    if (workflow.name) {
      return toPythonSafeSnakeCase(workflow.name);
    }
    const definition = workflow.exec_config.workflowRawData.definition;
    if (definition?.name) {
      return toPythonSafeSnakeCase(definition.name);
    }
    this.workflowContext.addError(
      new NodeDefinitionGenerationError(
        "Workflow definition name is required for inline workflows",
        "WARNING"
      )
    );
    return "inline_workflow_function";
  }

  private generateInlineWorkflowFiles(
    inlineWorkflows: InlineWorkflowFunctionArgs[]
  ): void {
    inlineWorkflows.forEach((workflow) => {
      const nestedWorkflowProject = this.getNestedWorkflowProject(workflow);

      this.inlineWorkflowsToGenerate.push({
        functionName: this.getInlineWorkflowFunctionName(workflow),
        workflowProject: nestedWorkflowProject,
      });
    });
  }

  getNodeDecorators(): python.Decorator[] | undefined {
    if (!this.nodeData.adornments) {
      return [];
    }
    return this.nodeData.adornments.map((adornment) =>
      python.decorator({
        callable: python.invokeMethod({
          methodReference: python.reference({
            name: adornment.base.name,
            attribute: ["wrap"],
            modulePath: adornment.base.module,
          }),
          arguments_: adornment.attributes.map((attr) =>
            python.methodArgument({
              name: attr.name,
              value: new WorkflowValueDescriptor({
                workflowValueDescriptor: attr.value,
                nodeContext: this.nodeContext,
                workflowContext: this.workflowContext,
                iterableConfig: { endWithComma: false },
              }),
            })
          ),
        }),
      })
    );
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(...this.nodeAttributes);

    if (this.nodeData.outputs.length > 0) {
      statements.push(
        new NodeOutputs({
          nodeOutputs: this.nodeData.outputs,
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
        })
      );
    }

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    if (!this.nodeData.outputs || this.nodeData.outputs.length === 0) {
      return undefined;
    }

    const outputDisplayEntries = this.nodeData.outputs.map((output) => ({
      key: python.reference({
        name: this.nodeContext.nodeClassName,
        modulePath: this.nodeContext.nodeModulePath,
        attribute: [OUTPUTS_CLASS_NAME, output.name],
      }),
      value: python.instantiateClass({
        classReference: python.reference({
          name: "NodeOutputDisplay",
          modulePath:
            this.workflowContext.sdkModulePathNames
              .NODE_DISPLAY_TYPES_MODULE_PATH,
        }),
        arguments_: [
          python.methodArgument({
            name: "id",
            value: python.TypeInstantiation.uuid(output.id),
          }),
          python.methodArgument({
            name: "name",
            value: python.TypeInstantiation.str(output.name),
          }),
        ],
      }),
    }));

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(outputDisplayEntries),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return undefined;
  }

  private getModulePath(): string[] {
    return this.nodeContext.nodeModulePath;
  }

  private isExcludedModulePath(): boolean {
    const baseModulePath = this.nodeData.base?.module;
    if (!baseModulePath) {
      return false;
    }

    return [
      this.workflowContext.sdkModulePathNames.CORE_NODES_MODULE_PATH,
      this.workflowContext.sdkModulePathNames.DISPLAYABLE_NODES_MODULE_PATH,
      this.workflowContext.sdkModulePathNames.EXPERIMENTAL_NODES_MODULE_PATH,
    ].some((excludedPath) =>
      excludedPath.every((part, index) => baseModulePath[index] === part)
    );
  }

  private async generateFunctionFile(
    functions: Array<FunctionArgs>
  ): Promise<void> {
    functions.forEach((f) => {
      this.functionsToGenerate.push({
        functionName: f.name,
        content: f.src,
      });
    });
  }

  public async persist(): Promise<void> {
    // Exclude nodes in the core, displayable, or experimental modules
    if (!this.isExcludedModulePath()) {
      const modulePath = this.getModulePath();
      const rootModulePath = this.workflowContext.getRootModulePath();

      // Build the full relative path from the module path
      // We are excluding the root module path since we need the
      // relative path from the root module
      const relativePath = `${modulePath
        .slice(rootModulePath.length - 1)
        .join("/")}.py`;

      this.workflowContext.addPythonCodeMergeableNodeFile(relativePath);
    }

    if (this.isNestedNode) {
      // Create __init__.py for node implementation
      const nodeInitFile = new InitFile({
        workflowContext: this.workflowContext,
        modulePath: this.nodeContext.nodeModulePath,
        statements: [this.generateNodeClass()],
      });

      // Create __init__.py for node display
      // We need to import nodes from those nested workflows to register the display classes
      const nestedImports: python.StarImport[] = [];
      this.inlineWorkflowsToGenerate.forEach((workflowFile) => {
        const workflowName = workflowFile.functionName;
        nestedImports.push(
          python.starImport({
            modulePath: [`.${workflowName}`, "nodes"],
          })
        );
      });

      const displayInitFile = new InitFile({
        workflowContext: this.workflowContext,
        modulePath: this.nodeContext.nodeDisplayModulePath,
        statements: this.generateNodeDisplayClasses(),
        imports: nestedImports.length > 0 ? nestedImports : undefined,
      });

      await Promise.all([
        nodeInitFile.persist(),
        displayInitFile.persist(),
        this.generateFunctionFiles(),
        this.generateInlineWorkflowProjects(),
      ]);
    } else {
      await super.persist();
    }
  }

  private async generateFunctionFiles(): Promise<void> {
    const absolutePath = this.workflowContext.absolutePathToOutputDirectory;
    const basePath = this.nodeContext.nodeModulePath.join("/");

    const nodeDir = join(absolutePath, basePath);
    await mkdir(nodeDir, { recursive: true });

    await Promise.all(
      this.functionsToGenerate.map(async (funcFile) => {
        const fileName = `${toPythonSafeSnakeCase(funcFile.functionName)}.py`;
        const filepath = join(nodeDir, fileName);

        await writeFile(filepath, funcFile.content);
      })
    );
  }

  private async generateInlineWorkflowProjects(): Promise<void> {
    // Generate nested workflow projects
    await Promise.all(
      this.inlineWorkflowsToGenerate.map(async (workflowFile) => {
        await workflowFile.workflowProject.generateCode();
      })
    );
  }
}
