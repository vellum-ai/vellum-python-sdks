import { BaseNode } from "./bases/base";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { GuardrailNodeContext } from "src/context/node-context/guardrail-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { DictInstantiation } from "src/generators/extensions/dict-instantiation";
import { Field } from "src/generators/extensions/field";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { GuardrailNode as GuardrailNodeType } from "src/types/vellum";

const INPUTS_PREFIX = "metric_inputs";
const STANDARD_METRIC_OUTPUT_KEYS = ["score", "normalized_score", "log"];

export class GuardrailNode extends BaseNode<
  GuardrailNodeType,
  GuardrailNodeContext
> {
  protected DEFAULT_TRIGGER = "AWAIT_ANY";
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (!this.nodeData.data.metricDefinitionId) {
      throw new NodeAttributeGenerationError(
        "metric_definition_id is required"
      );
    }

    statements.push(
      new Field({
        name: "metric_definition",
        initializer: new StrInstantiation(
          this.nodeData.data.metricDefinitionId
        ),
      })
    );

    statements.push(
      new Field({
        name: INPUTS_PREFIX,
        initializer: new DictInstantiation(
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

    if (!this.nodeData.data.releaseTag) {
      throw new NodeAttributeGenerationError("release_tag is required");
    }

    statements.push(
      new Field({
        name: "release_tag",
        initializer: new StrInstantiation(this.nodeData.data.releaseTag),
      })
    );

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      new Field({
        name: "target_handle_id",
        initializer: new UuidInstantiation(this.nodeData.data.targetHandleId),
      })
    );

    return statements;
  }

  protected getOutputDisplay(): Field {
    return new Field({
      name: "output_display",
      initializer: new DictInstantiation(
        (
          this.nodeContext.metricDefinitionsHistoryItem?.outputVariables ?? []
        ).map((output) => {
          const name = this.nodeContext.getNodeOutputNameById(output.id);
          const isStandardOutput = STANDARD_METRIC_OUTPUT_KEYS.includes(
            output.key
          );

          if (!name) {
            throw new NodeAttributeGenerationError(
              `Could not find output name for ${this.nodeContext.nodeClassName}.Outputs.${output.key} given output id ${output.id}`
            );
          }

          if (isStandardOutput) {
            // For standard outputs, use class reference
            return {
              key: new Reference({
                name: this.nodeContext.nodeClassName,
                modulePath: this.nodeContext.nodeModulePath,
                attribute: [OUTPUTS_CLASS_NAME, name],
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
                    value: new StrInstantiation(output.key),
                  }),
                ],
              }),
            };
          } else {
            // For non standard outputs, use a LazyReference
            return {
              key: new ClassInstantiation({
                classReference: new Reference({
                  name: "LazyReference",
                  modulePath: [
                    ...this.workflowContext.sdkModulePathNames
                      .WORKFLOWS_MODULE_PATH,
                    "references",
                  ],
                }),
                arguments_: [
                  new MethodArgument({
                    value: new StrInstantiation(
                      `${this.nodeContext.nodeClassName}.${OUTPUTS_CLASS_NAME}.${output.key}`
                    ),
                  }),
                ],
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
                    value: new StrInstantiation(output.key),
                  }),
                ],
              }),
            };
          }
        })
      ),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
