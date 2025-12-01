import { python } from "@fern-api/python-ast";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { PromptDeploymentNodeContext } from "src/context/node-context/prompt-deployment-node";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
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
          initializer: new ListInstantiation(
            this.nodeData.data.mlModelFallbacks.map(
              (model) => new StrInstantiation(model)
            )
          ),
        })
      );
    }

    if (this.nodeContext.promptDeploymentRelease) {
      statements.push(
        python.field({
          name: "deployment",
          initializer: new StrInstantiation(
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
        initializer: new StrInstantiation(nodeData.releaseTag),
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
              key: new StrInstantiation(key),
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
        key: new Reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "text"],
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
              value: python.TypeInstantiation.uuid(this.nodeData.data.outputId),
            }),
            new MethodArgument({
              name: "name",
              value: new StrInstantiation("text"),
            }),
          ],
        }),
      },
      {
        key: new Reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "results"],
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
              value: python.TypeInstantiation.uuid(
                this.nodeData.data.arrayOutputId
              ),
            }),
            new MethodArgument({
              name: "name",
              value: new StrInstantiation("results"),
            }),
          ],
        }),
      },
    ];

    if (jsonOutput) {
      outputDisplayEntries.push({
        key: new Reference({
          name: this.nodeContext.nodeClassName,
          modulePath: this.nodeContext.nodeModulePath,
          attribute: [OUTPUTS_CLASS_NAME, "json"],
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
              value: python.TypeInstantiation.uuid(jsonOutput.id),
            }),
            new MethodArgument({
              name: "name",
              value: new StrInstantiation("json"),
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
