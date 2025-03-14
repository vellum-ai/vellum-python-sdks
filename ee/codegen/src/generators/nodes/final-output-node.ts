import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { FinalOutputNodeContext } from "src/context/node-context/final-output-node";
import { BaseState } from "src/generators/base-state";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { FinalOutputNode as FinalOutputNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

export class FinalOutputNode extends BaseSingleFileNode<
  FinalOutputNodeType,
  FinalOutputNodeContext
> {
  protected getNodeBaseGenericTypes(): AstNode[] {
    const baseStateClassReference = new BaseState({
      workflowContext: this.workflowContext,
    });

    const primitiveOutputType = getVellumVariablePrimitiveType(
      this.nodeData.data.outputType
    );

    return [baseStateClassReference, primitiveOutputType];
  }

  getNodeClassBodyStatements(): AstNode[] {
    return [this.generateOutputsClass()];
  }

  private generateOutputsClass(): python.Class {
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

    const nodeInput = this.getNodeInputByName("node_input");

    if (nodeInput) {
      const outputField = python.field({
        name: "value",
        initializer: nodeInput,
      });
      outputsClass.add(outputField);
    }

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

    statements.push(
      python.field({
        name: "output_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.data.outputId),
      })
    );

    statements.push(
      python.field({
        name: "output_name",
        initializer: python.TypeInstantiation.str(this.nodeData.data.name),
      })
    );

    statements.push(
      python.field({
        name: "node_input_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.nodeInputId
        ),
      })
    );

    return statements;
  }

  protected getOutputDisplay(): python.Field {
    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict([
        {
          key: python.reference({
            name: this.nodeContext.nodeClassName,
            modulePath: this.nodeContext.nodeModulePath,
            attribute: [OUTPUTS_CLASS_NAME, "value"],
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
                  this.nodeData.data.outputId
                ),
              }),
              python.methodArgument({
                name: "name",
                value: python.TypeInstantiation.str("value"),
              }),
            ],
          }),
        },
      ]),
    });
  }

  protected getErrorOutputId(): undefined {
    return undefined;
  }
}
