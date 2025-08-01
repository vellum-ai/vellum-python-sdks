import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { OUTPUTS_CLASS_NAME, VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { PromptTemplateBlockExcludingFunctionDefinition } from "src/generators/base-prompt-block";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { FunctionDefinition } from "src/generators/function-definition";
import { BaseNode } from "src/generators/nodes/bases/base";
import { PromptParameters } from "src/generators/prompt-parameters-request";
import { StatefulPromptBlock } from "src/generators/stateful-prompt-block";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  FunctionDefinitionPromptTemplateBlock,
  InlinePromptNodeData,
  InlinePromptNode as InlinePromptNodeType,
  PlainTextPromptTemplateBlock,
  FunctionArgs,
  ToolArgs as FunctionsType,
  NodeAttribute,
} from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";
import { getCallableFunctions } from "src/utils/nodes";
import { isNilOrEmpty } from "src/utils/typing";

const INPUTS_PREFIX = "prompt_inputs";

export class InlinePromptNode extends BaseNode<
  InlinePromptNodeType,
  InlinePromptNodeContext
> {
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (this.nodeData.data.variant !== "INLINE") {
      throw new NodeAttributeGenerationError(
        `InlinePromptNode only supports INLINE variant. Received ${this.nodeData.data.variant}`
      );
    }

    const nodeData: InlinePromptNodeData = this.nodeData.data;
    const blocksExcludingFunctionDefinition =
      nodeData.execConfig.promptTemplateBlockData.blocks.filter(
        (
          block
        ): block is Exclude<
          PromptTemplateBlockExcludingFunctionDefinition,
          PlainTextPromptTemplateBlock
        > => block.blockType !== "FUNCTION_DEFINITION"
      );

    const functionDefinitions =
      nodeData.execConfig.promptTemplateBlockData.blocks.filter(
        (block): block is FunctionDefinitionPromptTemplateBlock =>
          block.blockType === "FUNCTION_DEFINITION"
      );

    const mlModelAttr = this.nodeData.attributes?.find(
      (attr) => attr.name === "ml_model"
    );

    // If we have the node attribute for ml model use it. Otherwise default to legacy way
    // of using ml model name
    if (mlModelAttr) {
      statements.push(
        python.field({
          name: "ml_model",
          initializer: new WorkflowValueDescriptor({
            nodeContext: this.nodeContext,
            workflowContext: this.workflowContext,
            workflowValueDescriptor: mlModelAttr.value,
          }),
        })
      );
    } else {
      statements.push(
        python.field({
          name: "ml_model",
          initializer: python.TypeInstantiation.str(nodeData.mlModelName),
        })
      );
    }

    statements.push(
      python.field({
        name: "blocks",
        initializer: python.TypeInstantiation.list(
          blocksExcludingFunctionDefinition.map((block) => {
            return new StatefulPromptBlock({
              workflowContext: this.workflowContext,
              promptBlock: block,
              inputVariableNameById: Object.fromEntries(
                this.nodeData.data.execConfig.inputVariables.map(
                  (inputVariable) => [inputVariable.id, inputVariable.key]
                )
              ),
            });
          }),
          {
            endWithComma: true,
          }
        ),
      })
    );

    const promptInputsAttribute = this.nodeData.attributes?.find(
      (attr) => attr.name === INPUTS_PREFIX
    );

    if (promptInputsAttribute) {
      statements.push(
        python.field({
          name: INPUTS_PREFIX,
          initializer: new WorkflowValueDescriptor({
            nodeContext: this.nodeContext,
            workflowContext: this.workflowContext,
            workflowValueDescriptor: promptInputsAttribute.value,
          }),
        })
      );
    } else if (this.nodeInputsByKey.size > 0) {
      statements.push(
        python.field({
          name: INPUTS_PREFIX,
          initializer: python.TypeInstantiation.dict(
            Array.from(this.nodeInputsByKey.entries()).map(([key, value]) => ({
              key: python.TypeInstantiation.str(key),
              value: value,
            })),
            {
              endWithComma: true,
            }
          ),
        })
      );
    }

    const functionsAttribute = this.nodeData.attributes?.find(
      (attr) => attr.name === "functions"
    );

    statements.push(
      ...this.getFunctionsFieldStatements(
        functionsAttribute,
        functionDefinitions
      )
    );

    statements.push(
      python.field({
        name: "parameters",
        initializer: new PromptParameters({
          promptParametersRequest: this.nodeData.data.execConfig.parameters,
        }),
      })
    );

    if (this.nodeData.data.execConfig.settings) {
      const timeout = this.nodeData.data.execConfig.settings.timeout;
      const streamEnabled =
        this.nodeData.data.execConfig.settings.streamEnabled;
      const args = [];
      if (!isNil(timeout)) {
        args.push(
          python.methodArgument({
            name: "timeout",
            value: python.TypeInstantiation.float(timeout),
          })
        );
      }
      if (!isNil(streamEnabled)) {
        args.push(
          python.methodArgument({
            name: "stream_enabled",
            value: python.TypeInstantiation.bool(streamEnabled),
          })
        );
      }
      if (!isNilOrEmpty(args)) {
        statements.push(
          python.field({
            name: "settings",
            initializer: python.instantiateClass({
              classReference: python.reference({
                name: "PromptSettings",
                modulePath: [...VELLUM_CLIENT_MODULE_PATH],
              }),
              arguments_: args,
            }),
          })
        );
      }
    }

    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "output_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.data.outputId),
      }),
      python.field({
        name: "array_output_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.arrayOutputId
        ),
      }),
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      })
    );

    return statements;
  }

  protected getOutputDisplay(): python.Field {
    const jsonOutput = this.nodeData.outputs?.find(
      (output) => output.type === "JSON"
    );

    const outputDisplayEntries = [
      {
        key: python.reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "text"],
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
              value: python.TypeInstantiation.uuid(this.nodeData.data.outputId),
            }),
            python.methodArgument({
              name: "name",
              value: python.TypeInstantiation.str("text"),
            }),
          ],
        }),
      },
      {
        key: python.reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "results"],
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
              value: python.TypeInstantiation.uuid(
                this.nodeData.data.arrayOutputId
              ),
            }),
            python.methodArgument({
              name: "name",
              value: python.TypeInstantiation.str("results"),
            }),
          ],
        }),
      },
    ];

    if (jsonOutput) {
      outputDisplayEntries.push({
        key: python.reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "json"],
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
              value: python.TypeInstantiation.uuid(jsonOutput.id),
            }),
            python.methodArgument({
              name: "name",
              value: python.TypeInstantiation.str("json"),
            }),
          ],
        }),
      });
    }

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(outputDisplayEntries),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }

  public getAdditionalFileStatements(): AstNode[] {
    const statements: AstNode[] = [];
    const functions = getCallableFunctions(this.nodeData);

    if (!isNilOrEmpty(functions)) {
      functions?.forEach((f) => {
        if (f.type === "CODE_EXECUTION" && !isNil((f as FunctionArgs).src)) {
          statements.push(python.codeBlock(f.src));
        }
      });
    }

    return statements;
  }

  private getFunctionsFieldStatements(
    functionsAttribute: NodeAttribute | undefined,
    functionDefinitions: FunctionDefinitionPromptTemplateBlock[]
  ): AstNode[] {
    const statements: AstNode[] = [];

    if (
      functionsAttribute &&
      functionsAttribute.value?.type === "CONSTANT_VALUE" &&
      functionsAttribute.value.value?.type === "JSON" &&
      Array.isArray(functionsAttribute.value.value.value)
    ) {
      const functions: FunctionsType = functionsAttribute.value.value.value;

      const codeExecutionFunctions = functions.filter(
        (f) => f.type === "CODE_EXECUTION" && !isNil((f as FunctionArgs).src)
      );

      if (codeExecutionFunctions.length > 0) {
        const modulePath = this.nodeContext.nodeModulePath;
        const fileName = modulePath[modulePath.length - 1] + ".py";
        const relativePath = `nodes/${fileName}`;

        this.workflowContext.addPythonCodeMergeableNodeFile(relativePath);

        statements.push(
          python.field({
            name: "functions",
            initializer: python.TypeInstantiation.list(
              codeExecutionFunctions.map((f) => {
                const funcName = toPythonSafeSnakeCase(f.name);
                return python.codeBlock(funcName);
              })
            ),
          })
        );
      }
    }

    if (
      functionsAttribute &&
      !this.isAttributeDefault(functionsAttribute.value, { defaultValue: null })
    ) {
      statements.push(
        python.field({
          name: "functions",
          initializer: new WorkflowValueDescriptor({
            nodeContext: this.nodeContext,
            workflowContext: this.workflowContext,
            workflowValueDescriptor: functionsAttribute.value,
          }),
        })
      );
    } else if (functionDefinitions.length > 0) {
      statements.push(
        python.field({
          name: "functions",
          initializer: python.TypeInstantiation.list(
            functionDefinitions.map(
              (functionDefinition) =>
                new FunctionDefinition({ functionDefinition })
            ),
            {
              endWithComma: true,
            }
          ),
        })
      );
    }

    return statements;
  }
}
