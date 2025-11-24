import { python } from "@fern-api/python-ast";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { BaseNode } from "src/generators/nodes/bases/base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { DeploymentPromptNodeData, PromptNode } from "src/types/vellum";

const INPUTS_PREFIX = "prompt_inputs";

export class PromptDeploymentNode extends BaseNode<
  PromptNode,
  PromptDeploymentNodeContext
> {
  protected DEFAULT_TRIGGER = "AWAIT_ANY";
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (this.nodeData.data.variant !== "DEPLOYMENT") {
      throw new NodeDefinitionGenerationError(
        `PromptDeploymentNode only supports DEPLOYMENT variant. Received ${this.nodeData.data.variant}`
      );
    }

    const nodeData: DeploymentPromptNodeData = this.nodeData.data;
    if (
      this.nodeData.data.mlModelFallbacks &&
      this.nodeData.data.mlModelFallbacks.length > 0
    ) {
      statements.push(
        python.field({
          name: "ml_model_fallbacks",
          initializer: python.TypeInstantiation.list(
            this.nodeData.data.mlModelFallbacks.map((model) =>
              python.TypeInstantiation.str(model)
            )
          ),
        })
      );
    }

    if (this.nodeContext.promptDeploymentRelease) {
      statements.push(
        python.field({
          name: "deployment",
          initializer: python.TypeInstantiation.str(
            this.nodeContext.promptDeploymentRelease.deployment.name
          ),
        })
      );
    } else {
      statements.push(
        python.field({
          name: "deployment",
          initializer: python.TypeInstantiation.uuid(
            this.nodeData.data.promptDeploymentId
          ),
        })
      );
    }

    statements.push(
      python.field({
        name: "release_tag",
        initializer: python.TypeInstantiation.str(nodeData.releaseTag),
      })
    );

    const promptInputsAttribute = this.nodeData.attributes?.find(
      (attribute) => attribute.name === INPUTS_PREFIX
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

    return statements;
  }

  protected getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
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
