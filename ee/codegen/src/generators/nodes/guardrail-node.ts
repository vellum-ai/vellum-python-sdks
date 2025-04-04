import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { GuardrailNodeContext } from "src/context/node-context/guardrail-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { GuardrailNode as GuardrailNodeType } from "src/types/vellum";

const INPUTS_PREFIX = "metric_inputs";

export class GuardrailNode extends BaseSingleFileNode<
  GuardrailNodeType,
  GuardrailNodeContext
> {
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
      python.field({
        name: "metric_definition",
        initializer: python.TypeInstantiation.str(
          this.nodeData.data.metricDefinitionId
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

    if (!this.nodeData.data.releaseTag) {
      throw new NodeAttributeGenerationError("release_tag is required");
    }

    statements.push(
      python.field({
        name: "release_tag",
        initializer: python.TypeInstantiation.str(
          this.nodeData.data.releaseTag
        ),
      })
    );

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    statements.push(
      python.field({
        name: "label",
        initializer: python.TypeInstantiation.str(this.nodeData.data.label),
      })
    );

    statements.push(
      python.field({
        name: "node_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.id),
      })
    );

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
    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(
        (
          this.nodeContext.metricDefinitionsHistoryItem?.outputVariables ?? []
        ).map((output) => {
          const name = this.nodeContext.getNodeOutputNameById(output.id);

          if (!name) {
            throw new NodeAttributeGenerationError(
              `Could not find output name for ${this.nodeContext.nodeClassName}.Outputs.${output.key} given output id ${output.id}`
            );
          }
          return {
            key: python.reference({
              name: this.nodeContext.nodeClassName,
              modulePath: this.nodeContext.nodeModulePath,
              attribute: [OUTPUTS_CLASS_NAME, name],
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
                  value: python.TypeInstantiation.str(output.key),
                }),
              ],
            }),
          };
        })
      ),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
