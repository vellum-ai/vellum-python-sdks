import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { PromptTemplateBlockExcludingFunctionDefinition } from "src/generators/base-prompt-block";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { FunctionDefinition } from "src/generators/function-definition";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { PromptBlock } from "src/generators/prompt-block";
import { PromptParameters } from "src/generators/prompt-parameters-request";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  InlinePromptNode as InlinePromptNodeType,
  FunctionDefinitionPromptTemplateBlock,
  InlinePromptNodeData,
  PlainTextPromptTemplateBlock,
} from "src/types/vellum";

const INPUTS_PREFIX = "prompt_inputs";

export class InlinePromptNode extends BaseSingleFileNode<
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
            return new PromptBlock({
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

    if (functionDefinitions.length > 0) {
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

    statements.push(
      python.field({
        name: "parameters",
        initializer: new PromptParameters({
          promptParametersRequest: this.nodeData.data.execConfig.parameters,
        }),
      })
    );

    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      }),
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      }),
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
}
