import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { DeploymentPromptNodeData, PromptNode } from "src/types/vellum";

export class PromptDeploymentNode extends BaseSingleFileNode<
  PromptNode,
  PromptDeploymentNodeContext
> {
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

    if (this.nodeContext.deploymentHistoryItem) {
      statements.push(
        python.field({
          name: "deployment",
          initializer: python.TypeInstantiation.str(
            this.nodeContext.deploymentHistoryItem.name
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

    statements.push(
      python.field({
        name: "prompt_inputs",
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
