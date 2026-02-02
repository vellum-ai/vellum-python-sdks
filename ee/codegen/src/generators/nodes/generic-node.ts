import { mkdir, writeFile } from "fs/promises";
import { join } from "path";

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
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { Decorator } from "src/generators/extensions/decorator";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { MethodInvocation } from "src/generators/extensions/method-invocation";
import { Reference } from "src/generators/extensions/reference";
import { StarImport } from "src/generators/extensions/star-import";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { WrappedCall } from "src/generators/extensions/wrapped-call";
import { InitFile } from "src/generators/init-file";
import { Json } from "src/generators/json";
import { NodeOutputs } from "src/generators/node-outputs";
import { BaseNode } from "src/generators/nodes/bases/base";
import { AttributeType, NODE_ATTRIBUTES } from "src/generators/nodes/constants";
import { PromptBlock } from "src/generators/prompt-block";
import { PromptParameters } from "src/generators/prompt-parameters-request";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { WorkflowProjectGenerator } from "src/project";
import {
  WorkflowValueDescriptorSerializer,
  WorkflowVersionExecConfigSerializer,
} from "src/serializers/vellum";
import {
  ComposioToolFunctionArgs,
  FunctionArgs,
  GenericNode as GenericNodeType,
  InlineWorkflowFunctionArgs,
  MCPServerFunctionArgs,
  ToolArgs,
  VellumIntegrationToolFunctionArgs,
  WorkflowDeploymentFunctionArgs,
  WorkflowRawData,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
  WorkflowVersionExecConfig,
} from "src/types/vellum";
import {
  createPythonClassName,
  toPythonSafeSnakeCase,
  toValidPythonIdentifier,
} from "src/utils/casing";
import { findNodeDefinitionByBaseClassName } from "src/utils/node-definitions";

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

          const functionHandlers: Record<
            ToolArgs["type"],
            (f: ToolArgs) => AstNode | null
          > = {
            CODE_EXECUTION: (f) => this.handleCodeExecutionFunction(f),
            INLINE_WORKFLOW: (f) => this.handleInlineWorkflowFunction(f),
            WORKFLOW_DEPLOYMENT: (f) =>
              this.handleWorkflowDeploymentFunction(f),
            COMPOSIO: (f) => this.handleComposioFunction(f),
            MCP_SERVER: (f) => this.handleMCPServerFunction(f),
            VELLUM_INTEGRATION: (f) => this.handleVellumIntegrationFunction(f),
          };

          if (
            value?.type === "CONSTANT_VALUE" &&
            value.value?.type === "JSON" &&
            Array.isArray(value.value.value)
          ) {
            const functions: ToolArgs[] = value.value.value;
            const functionReferences: AstNode[] = [];

            functions.forEach((f) => {
              const handler = functionHandlers[f.type];
              if (!handler) {
                this.workflowContext.addError(
                  new NodeDefinitionGenerationError(
                    `Unsupported function type: ${JSON.stringify(f)}.`,
                    "WARNING"
                  )
                );
                return;
              }

              const functionReference = handler(f);

              if (functionReference) {
                functionReferences.push(functionReference);
              }
            });

            nodeAttributesStatements.push(
              new Field({
                name: toValidPythonIdentifier(attribute.name, "attr"),
                initializer: new ListInstantiation(functionReferences),
              })
            );
          } else if (value?.type === "ARRAY_REFERENCE") {
            // Handle ARRAY_REFERENCE format (e.g., MCPServer with EnvironmentVariableReference)
            // Process each item using the same handler pattern as CONSTANT_VALUE
            // Order is preserved by processing each item inline.
            const items = value.items || [];
            const functionReferences: AstNode[] = [];

            // Process each item in order to preserve function ordering
            items.forEach((item) => {
              if (
                item.type === "CONSTANT_VALUE" &&
                item.value?.type === "JSON" &&
                item.value.value &&
                typeof item.value.value === "object" &&
                "type" in item.value.value
              ) {
                // This is a ToolArgs object, use the handler pattern
                // which handles all function types (CODE_EXECUTION, INLINE_WORKFLOW, etc.)
                const toolArg = item.value.value as ToolArgs;
                const handler = functionHandlers[toolArg.type];
                if (handler) {
                  const functionReference = handler(toolArg);
                  if (functionReference) {
                    functionReferences.push(functionReference);
                  }
                } else {
                  this.workflowContext.addError(
                    new NodeDefinitionGenerationError(
                      `Unsupported function type in ARRAY_REFERENCE: ${JSON.stringify(
                        toolArg
                      )}`,
                      "WARNING"
                    )
                  );
                }
              } else {
                // For other items (like DICTIONARY_REFERENCE for MCPServer),
                // use WorkflowValueDescriptor directly
                functionReferences.push(
                  new WorkflowValueDescriptor({
                    nodeContext: this.nodeContext,
                    workflowContext: this.workflowContext,
                    workflowValueDescriptor: item,
                  })
                );
              }
            });

            nodeAttributesStatements.push(
              new Field({
                name: toValidPythonIdentifier(attribute.name, "attr"),
                initializer: new ListInstantiation(functionReferences),
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
              new Field({
                name: attribute.name,
                initializer: new ListInstantiation(
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
              new Field({
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
            new Field({
              name: toPythonSafeSnakeCase(attribute.name),
              initializer: new WorkflowValueDescriptor({
                nodeContext: this.nodeContext,
                workflowValueDescriptor: attribute.value,
                workflowContext: this.workflowContext,
                attributeConfig: attribute.schema
                  ? {
                      lhs: new Reference({ name: "", modulePath: [] }),
                      schema: attribute.schema,
                    }
                  : undefined,
              }),
            })
          );
      }
    });

    return nodeAttributesStatements;
  }

  private handleCodeExecutionFunction(f: ToolArgs): AstNode {
    const codeExecutionFunction = f as FunctionArgs;
    this.generateFunctionFile([codeExecutionFunction]);
    const snakeName = toPythonSafeSnakeCase(codeExecutionFunction.name);
    // Use toValidPythonIdentifier to ensure the name is safe for Python references
    // but preserve original casing when possible (see APO-1372)
    const safeName = toValidPythonIdentifier(codeExecutionFunction.name);
    const functionReference = new Reference({
      name: safeName, // Use safe Python identifier that preserves original casing
      modulePath: [`.${snakeName}`], // Import from snake_case module
    });

    // Check if function has inputs or examples that need to be wrapped with tool()
    const parsedInputs = this.parseToolInputs(codeExecutionFunction);
    // Read examples from definition.parameters.examples (JSON Schema examples keyword)
    const parameters = codeExecutionFunction.definition?.parameters as
      | Record<string, unknown>
      | undefined;
    const examples =
      (parameters?.examples as Array<Record<string, unknown>>) ?? null;
    const hasInputs = parsedInputs && Object.keys(parsedInputs).length > 0;
    const hasExamples = Array.isArray(examples) && examples.length > 0;

    if (hasInputs || hasExamples) {
      // Wrap the function reference with tool(...)(func)
      const wrapper = this.getToolInvocation(parsedInputs, examples);
      return new WrappedCall({
        wrapper,
        inner: functionReference,
      });
    }

    return functionReference;
  }

  private handleInlineWorkflowFunction(f: ToolArgs): AstNode | null {
    const inlineWorkflow = f as InlineWorkflowFunctionArgs;
    const rawExecConfig =
      inlineWorkflow.exec_config as unknown as WorkflowVersionExecConfigSerializer.Raw;
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
      return null;
    }

    const workflowVersionExecConfig: WorkflowVersionExecConfig =
      workflowVersionExecConfigResult.value;
    const workflow: InlineWorkflowFunctionArgs = {
      type: "INLINE_WORKFLOW",
      name: inlineWorkflow.name,
      description: inlineWorkflow.description,
      exec_config: workflowVersionExecConfig,
      module_name: inlineWorkflow.module_name,
    };

    // Generate inline workflow file directly
    const nestedWorkflowProject = this.getNestedWorkflowProject(workflow);
    const workflowName = this.getInlineWorkflowFunctionName(workflow);
    if (workflowName) {
      this.inlineWorkflowsToGenerate.push({
        functionName: workflowName,
        workflowProject: nestedWorkflowProject,
      });

      const workflowClassName =
        nestedWorkflowProject.workflowContext.workflowClassName;
      return new Reference({
        name: workflowClassName,
        modulePath: [`.${workflowName}`, GENERATED_WORKFLOW_MODULE_NAME],
      });
    }

    return null;
  }

  private handleWorkflowDeploymentFunction(f: ToolArgs): AstNode {
    const workflowDeployment = f as WorkflowDeploymentFunctionArgs;
    const workflowDeploymentName = workflowDeployment.deployment;
    const args: MethodArgument[] = [
      new MethodArgument({
        name: "deployment",
        value: new StrInstantiation(workflowDeploymentName),
      }),
    ];

    if (workflowDeployment.release_tag !== null) {
      args.push(
        new MethodArgument({
          name: "release_tag",
          value: new StrInstantiation(workflowDeployment.release_tag),
        })
      );
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "DeploymentDefinition",
        modulePath: ["vellum", "workflows", "types", "definition"],
      }),
      arguments_: args,
    });
  }

  private handleComposioFunction(f: ToolArgs): AstNode {
    const composioTool = f as ComposioToolFunctionArgs;

    // Validate required fields and provide fallbacks for missing fields
    // Frontend sends integration_name and tool_slug, but backend sends toolkit and action
    const toolkit =
      composioTool.integration_name || composioTool.toolkit || "UNKNOWN";
    const action = composioTool.tool_slug || composioTool.action || "UNKNOWN";
    const description = composioTool.description || "UNKNOWN";

    const args: MethodArgument[] = [
      new MethodArgument({
        name: "toolkit",
        value: new StrInstantiation(toolkit),
      }),
      new MethodArgument({
        name: "action",
        value: new StrInstantiation(action),
      }),
      new MethodArgument({
        name: "description",
        value: new StrInstantiation(description),
      }),
    ];

    if (composioTool.user_id != null) {
      args.push(
        new MethodArgument({
          name: "user_id",
          value: new StrInstantiation(composioTool.user_id),
        })
      );
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "ComposioToolDefinition",
        modulePath: VELLUM_WORKFLOW_DEFINITION_PATH,
      }),
      arguments_: args,
    });
  }

  private handleMCPServerFunction(f: ToolArgs): AstNode {
    const mcpServerFunction = f as MCPServerFunctionArgs;

    const arguments_: MethodArgument[] = [
      new MethodArgument({
        name: "name",
        value: new StrInstantiation(mcpServerFunction.name),
      }),
      new MethodArgument({
        name: "url",
        value: new StrInstantiation(mcpServerFunction.url),
      }),
    ];

    if (mcpServerFunction.authorization_type) {
      arguments_.push(
        new MethodArgument({
          name: "authorization_type",
          value: new Reference({
            name: "AuthorizationType",
            modulePath: [
              ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
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
        new MethodArgument({
          name: "bearer_token_value",
          value: new WorkflowValueDescriptor({
            workflowValueDescriptor: {
              type: "ENVIRONMENT_VARIABLE",
              environmentVariable: mcpServerFunction.bearer_token_value,
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
        new MethodArgument({
          name: "api_key_header_key",
          value: new StrInstantiation(mcpServerFunction.api_key_header_key),
        })
      );
    }

    if (
      mcpServerFunction.authorization_type === "API_KEY" &&
      mcpServerFunction.api_key_header_value
    ) {
      arguments_.push(
        new MethodArgument({
          name: "api_key_header_value",
          value: new WorkflowValueDescriptor({
            workflowValueDescriptor: {
              type: "ENVIRONMENT_VARIABLE",
              environmentVariable: mcpServerFunction.api_key_header_value,
            },
            nodeContext: this.nodeContext,
            workflowContext: this.workflowContext,
          }),
        })
      );
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "MCPServer",
        modulePath: VELLUM_WORKFLOW_DEFINITION_PATH,
      }),
      arguments_,
    });
  }

  private handleVellumIntegrationFunction(f: ToolArgs): AstNode {
    const integrationTool = f as VellumIntegrationToolFunctionArgs;

    const args: MethodArgument[] = [
      new MethodArgument({
        name: "provider",
        value: new StrInstantiation(integrationTool.provider || "COMPOSIO"),
      }),
      new MethodArgument({
        name: "integration_name",
        value: new StrInstantiation(
          integrationTool.integration_name || "UNKNOWN"
        ),
      }),
      new MethodArgument({
        name: "name",
        value: new StrInstantiation(integrationTool.name || "UNKNOWN"),
      }),
      new MethodArgument({
        name: "description",
        value: new StrInstantiation(integrationTool.description || "UNKNOWN"),
      }),
    ];

    if (integrationTool.toolkit_version != null) {
      args.push(
        new MethodArgument({
          name: "toolkit_version",
          value: new StrInstantiation(integrationTool.toolkit_version),
        })
      );
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "VellumIntegrationToolDefinition",
        modulePath: VELLUM_WORKFLOW_DEFINITION_PATH,
      }),
      arguments_: args,
    });
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
        stateVariables: workflow.exec_config.stateVariables ?? [],
        outputVariables: workflow.exec_config.outputVariables,
      },
      moduleName: nestedWorkflowContext.moduleName,
      workflowContext: nestedWorkflowContext,
    });
  }

  private getInlineWorkflowFunctionName(
    workflow: InlineWorkflowFunctionArgs
  ): string {
    // Use the module_name if available (from serialization) to match the original module path
    if (workflow.module_name) {
      return workflow.module_name;
    }
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

  getNodeDecorators(): Decorator[] | undefined {
    if (!this.nodeData.adornments) {
      return [];
    }
    return this.nodeData.adornments.map(
      (adornment) =>
        new Decorator({
          callable: new MethodInvocation({
            methodReference: new Reference({
              name: adornment.base.name,
              attribute: ["wrap"],
              modulePath: adornment.base.module,
            }),
            arguments_: adornment.attributes.map(
              (attr) =>
                new MethodArgument({
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

  private hasRedundantOutputs(): boolean {
    const baseClassName = this.nodeData.base?.name;
    if (!baseClassName) {
      return false;
    }
    const baseNodeDef = findNodeDefinitionByBaseClassName(baseClassName);
    if (!baseNodeDef?.outputs || !this.nodeData.outputs) {
      return false;
    }
    // Check if all outputs in nodeData match the base node definition outputs
    // Compare by name, type, and value to ensure customized outputs are preserved
    // Base node definitions always have value: null, so we check if any output has a non-null value
    // Treat workflow outputs as a subset - if all workflow outputs exist in base and match,
    // it's redundant (no need to generate an Outputs class override)
    const baseOutputsByName = new Map(
      baseNodeDef.outputs.map((o) => [o.name, o])
    );

    // If workflow has more outputs than base, it's not redundant (has custom outputs)
    if (this.nodeData.outputs.length > baseNodeDef.outputs.length) {
      return false;
    }

    return this.nodeData.outputs.every((output) => {
      const baseOutput = baseOutputsByName.get(output.name);
      if (!baseOutput) {
        // Output doesn't exist in base - not redundant (custom output)
        return false;
      }
      if (baseOutput.type !== output.type) {
        // Type mismatch - not redundant (customized output)
        return false;
      }
      // Only redundant if value is null/undefined (not customized)
      return output.value === null || output.value === undefined;
    });
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(...this.nodeAttributes);

    if (this.nodeData.outputs.length > 0 && !this.hasRedundantOutputs()) {
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

  protected getOutputDisplay(): Field | undefined {
    if (!this.nodeData.outputs || this.nodeData.outputs.length === 0) {
      return undefined;
    }

    const outputDisplayEntries = this.nodeData.outputs.map((output) => ({
      key: new Reference({
        name: this.nodeContext.nodeClassName,
        modulePath: this.nodeContext.nodeModulePath,
        attribute: [OUTPUTS_CLASS_NAME, output.name],
      }),
      value: new ClassInstantiation({
        classReference: new Reference({
          name: "NodeOutputDisplay",
          modulePath:
            this.workflowContext.sdkModulePathNames
              .NODE_DISPLAY_TYPES_MODULE_PATH,
        }),
        arguments_: [
          new MethodArgument({
            name: "id",
            value: new UuidInstantiation(output.id),
          }),
          new MethodArgument({
            name: "name",
            value: new StrInstantiation(output.name),
          }),
        ],
      }),
    }));

    return new Field({
      name: "output_display",
      initializer: new DictInstantiation(outputDisplayEntries),
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
      const nodeInitFile = new InitFile({
        workflowContext: this.workflowContext,
        modulePath: this.nodeContext.nodeModulePath,
        statements: [this.generateNodeClass()],
      });

      const nestedImports: StarImport[] = [];
      this.inlineWorkflowsToGenerate.forEach((workflowFile) => {
        const workflowName = workflowFile.functionName;
        nestedImports.push(
          new StarImport({
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

  /**
   * Parses the tool inputs from a function definition.
   * Returns null if there are no inputs or if parsing fails.
   */
  private parseToolInputs(
    f: FunctionArgs
  ): Record<string, WorkflowValueDescriptorType> | null {
    const inputs = f.definition?.inputs;
    if (!f.definition || !inputs) {
      return null;
    }

    const parsedInputs: Record<string, WorkflowValueDescriptorType> = {};
    Object.entries(inputs).forEach(([inputName, inputDef]) => {
      const inputResult = WorkflowValueDescriptorSerializer.parse(inputDef);
      if (inputResult.ok) {
        parsedInputs[inputName] = inputResult.value;
      } else {
        this.workflowContext.addError(
          new NodeDefinitionGenerationError(
            `Failed to parse input '${inputName}': ${JSON.stringify(
              inputResult.errors
            )}`
          )
        );
      }
    });

    if (Object.keys(parsedInputs).length === 0) {
      return null;
    }

    return parsedInputs;
  }

  /**
   * Creates a tool(inputs={...}, examples=[...]) method invocation for wrapping function references.
   */
  private getToolInvocation(
    inputs: Record<string, WorkflowValueDescriptorType> | null,
    examples: Array<Record<string, unknown>> | null
  ): MethodInvocation {
    const arguments_: MethodArgument[] = [];

    // Build dict entries for the inputs parameter if provided
    if (inputs && Object.keys(inputs).length > 0) {
      const dictEntries = Object.entries(inputs).map(
        ([inputName, inputDef]) => {
          const workflowValueDescriptor = new WorkflowValueDescriptor({
            workflowValueDescriptor: inputDef,
            nodeContext: this.nodeContext,
            workflowContext: this.workflowContext,
          });

          return {
            key: new StrInstantiation(inputName),
            value: workflowValueDescriptor,
          };
        }
      );

      const inputsDict = new DictInstantiation(dictEntries, {
        endWithComma: true,
      });

      arguments_.push(
        new MethodArgument({
          name: "inputs",
          value: inputsDict,
        })
      );
    }

    // Build list entries for the examples parameter if provided
    if (examples && examples.length > 0) {
      const exampleDicts = examples.map((example) => {
        const dictEntries = Object.entries(example).map(([key, value]) => ({
          key: new StrInstantiation(key),
          value: new Json(value),
        }));
        return new DictInstantiation(dictEntries, {
          endWithComma: true,
        });
      });

      arguments_.push(
        new MethodArgument({
          name: "examples",
          value: new ListInstantiation(exampleDicts, {
            endWithComma: true,
          }),
        })
      );
    }

    return new MethodInvocation({
      methodReference: new Reference({
        name: "tool",
        modulePath: ["vellum", "workflows", "utils", "functions"],
      }),
      arguments_,
    });
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
