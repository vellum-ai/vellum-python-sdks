import { python } from "@fern-api/python-ast";

import { OUTPUTS_CLASS_NAME } from "src/constants";
import { FinalOutputNodeContext } from "src/context/node-context/final-output-node";
import { Class, PythonType } from "src/generators/extensions";
import { AstNode } from "src/generators/extensions/ast-node";
import { BaseNode } from "src/generators/nodes/bases/base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { FinalOutputNode as FinalOutputNodeType } from "src/types/vellum";
import {
  getVellumVariablePrimitiveType,
  jsonSchemaToType,
} from "src/utils/vellum-variables";

export class FinalOutputNode extends BaseNode<
  FinalOutputNodeType,
  FinalOutputNodeContext
> {
  protected DEFAULT_TRIGGER = "AWAIT_ANY";
  protected getNodeBaseGenericTypes(): AstNode[] {
    const stateType = this.getStateTypeOrBaseState();

    let primitiveOutputType: python.Type | PythonType;
    const valueOutput = this.nodeData.outputs?.find(
      (output) => output.name === "value"
    );

    if (valueOutput?.schema) {
      primitiveOutputType = jsonSchemaToType(valueOutput.schema);
    } else {
      primitiveOutputType = getVellumVariablePrimitiveType(
        this.nodeData.data.outputType
      );
    }

    return [stateType, primitiveOutputType];
  }

  getNodeClassBodyStatements(): AstNode[] {
    return [this.generateOutputsClass()];
  }

  private generateOutputsClass(): Class {
    const nodeBaseClassRef = this.getNodeBaseClass();
    const outputsClass = new Class({
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

    const descriptors = this.nodeData.outputs?.map((output) => output.value);

    if (descriptors && descriptors.length > 0) {
      descriptors.forEach((descriptor) => {
        if (descriptor) {
          const workflowValueDescriptor = new WorkflowValueDescriptor({
            nodeContext: this.nodeContext,
            workflowValueDescriptor: descriptor,
            workflowContext: this.workflowContext,
          });

          const outputField = python.field({
            name: "value",
            initializer: workflowValueDescriptor,
          });
          outputsClass.add(outputField);
        }
      });
    } else {
      const nodeInput = this.getNodeInputByName("node_input");

      if (nodeInput) {
        const outputField = python.field({
          name: "value",
          initializer: nodeInput,
        });
        outputsClass.add(outputField);
      }
    }
    return outputsClass;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

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
        name: "output_name",
        initializer: python.TypeInstantiation.str(this.nodeData.data.name),
      })
    );

    return statements;
  }

  protected getOutputDisplay(): python.Field {
    return python.field({
      name: "output_display",
      initializer: python.TypeInstantiation.dict(
        [
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
        ],
        { endWithComma: true }
      ),
    });
  }

  protected getErrorOutputId(): undefined {
    return undefined;
  }
}
