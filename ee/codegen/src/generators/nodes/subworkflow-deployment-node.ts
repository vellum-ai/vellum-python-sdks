import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { SubworkflowDeploymentNodeContext } from "src/context/node-context/subworkflow-deployment-node";
import {
  NodeAttributeGenerationError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { codegen } from "src/index";
import { SubworkflowNode as SubworkflowNodeType } from "src/types/vellum";

export class SubworkflowDeploymentNode extends BaseSingleFileNode<
  SubworkflowNodeType,
  SubworkflowDeploymentNodeContext
> {
  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    if (this.nodeData.data.variant !== "DEPLOYMENT") {
      throw new NodeDefinitionGenerationError(
        `SubworkflowDeploymentNode only supports DEPLOYMENT variant. Received ${this.nodeData.data.variant}`
      );
    }

    if (!this.nodeContext.workflowDeploymentHistoryItem) {
      throw new NodeDefinitionGenerationError(
        "Workflow Deployment History Item is not set"
      );
    }

    statements.push(
      python.field({
        name: "deployment",
        initializer: python.TypeInstantiation.str(
          this.nodeContext.workflowDeploymentHistoryItem.name
        ),
      })
    );

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
        name: "subworkflow_inputs",
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

    statements.push(this.generateOutputsClass());

    return statements;
  }

  private generateOutputsClass(): python.Class {
    if (!this.nodeContext.workflowDeploymentHistoryItem) {
      throw new NodeDefinitionGenerationError(
        "Workflow Deployment History Item is not set"
      );
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

    this.nodeContext.workflowDeploymentHistoryItem.outputVariables.forEach(
      (output) => {
        const outputName = this.nodeContext.getNodeOutputNameById(output.id);
        if (outputName) {
          outputsClass.add(
            codegen.vellumVariable({
              variable: { name: outputName, type: output.type, id: output.id },
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

  protected getOutputDisplay(): python.Field {
    if (!this.nodeContext.workflowDeploymentHistoryItem) {
      throw new NodeDefinitionGenerationError(
        "Workflow Deployment History Item is not set"
      );
    }

    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(
        this.nodeContext.workflowDeploymentHistoryItem.outputVariables.map(
          (output) => {
            const outputName = this.nodeContext.getNodeOutputNameById(
              output.id
            );
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
          }
        )
      ),
    });
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
