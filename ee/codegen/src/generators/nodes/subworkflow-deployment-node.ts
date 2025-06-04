import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import {
  NodeAttributeGenerationError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import { BaseNode } from "src/generators/nodes/bases/base";
import { codegen } from "src/index";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";

const INPUTS_PREFIX = "subworkflow_inputs";

export class SubworkflowDeploymentNode extends BaseNode<
  SubworkflowNodeType,
  SubworkflowDeploymentNodeContext
> {
  protected getNodeAttributeNameByNodeInputKey(nodeInputKey: string): string {
    return `${INPUTS_PREFIX}.${nodeInputKey}`;
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (this.nodeData.data.variant !== "DEPLOYMENT") {
      throw new NodeDefinitionGenerationError(
        `SubworkflowDeploymentNode only supports DEPLOYMENT variant. Received ${this.nodeData.data.variant}`
      );
    }

    if (!this.nodeContext.workflowDeploymentRelease) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          `Failed to generate attribute: ${this.nodeData.data.label}.deployment`
        )
      );
    } else {
      statements.push(
        python.field({
          name: "deployment",
          initializer: python.TypeInstantiation.str(
            this.nodeContext.workflowDeploymentRelease.deployment.name
          ),
        })
      );
    }

    statements.push(
      python.field({
        name: "release_tag",
        initializer: python.TypeInstantiation.str(
          this.nodeData.data.releaseTag
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

    const outputsClass = this.generateOutputsClass();
    if (outputsClass) {
      statements.push(outputsClass);
    }

    return statements;
  }

  private generateOutputsClass(): python.Class | null {
    if (!this.nodeContext.workflowDeploymentRelease) {
      this.workflowContext.addError(
        new NodeAttributeGenerationError(
          `Failed to generate ${this.nodeData.data.label}.Outputs class`
        )
      );
      return null;
    }

    const nodeBaseClassRef = this.getNodeBaseClass();
    const outputsClass = python.class_({
      name: OUTPUTS_CLASS_NAME,
      extends_: [
        python.reference({
          name: nodeBaseClassRef.name,
          modulePath: nodeBaseClassRef.modulePath,
          alias: nodeBaseClassRef.alias,
          attribute: [OUTPUTS_CLASS_NAME],
        }),
      ],
    });

    this.nodeContext.workflowDeploymentRelease.workflowVersion.outputVariables.forEach(
      (output) => {
        const outputName = this.nodeContext.getNodeOutputNameById(output.id);
        if (outputName) {
          outputsClass.add(
            codegen.vellumVariable({
              variable: {
                name: outputName,
                type: output.type,
                id: output.id,
                required: output.required,
              },
              defaultRequired: true,
            })
          );
        }
      }
    );

    return outputsClass;
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

  protected getOutputDisplay(): python.Field | undefined {
    if (!this.nodeContext.workflowDeploymentRelease) {
      this.workflowContext.addError(
        new NodeDefinitionGenerationError(
          `Failed to generate \`output_display\` for ${this.nodeData.data.label}`,
          "WARNING"
        )
      );
    }

    const outputVariables =
      this.nodeContext.workflowDeploymentRelease?.workflowVersion
        .outputVariables ?? [];

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(
        outputVariables.map((output) => {
          const outputName = this.nodeContext.getNodeOutputNameById(output.id);
          if (!outputName) {
            throw new NodeAttributeGenerationError(
              `Could not find output name for ${this.nodeContext.nodeClassName}.Outputs.${output.key} given output id ${output.id}`
            );
          }
          return {
            key: python.reference({
              name: this.nodeContext.nodeClassName,
              modulePath: this.nodeContext.nodeModulePath,
              attribute: [OUTPUTS_CLASS_NAME, outputName],
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
