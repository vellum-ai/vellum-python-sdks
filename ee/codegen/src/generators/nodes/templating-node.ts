import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { BaseState } from "src/generators/base-state";
import { NodeInputValuePointer } from "src/generators/node-inputs/node-input-value-pointer";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { TemplatingNode as TemplatingNodeType } from "src/types/vellum";
import { getVellumVariablePrimitiveType } from "src/utils/vellum-variables";

export class TemplatingNode extends BaseSingleFileNode<
  TemplatingNodeType,
  TemplatingNodeContext
> {
  baseNodeClassName = "TemplatingNode";
  baseNodeDisplayClassName = "BaseTemplatingNodeDisplay";

  protected getNodeBaseGenericTypes(): AstNode[] {
    const baseStateClassReference = new BaseState({
      workflowContext: this.workflowContext,
    });

    const primitiveOutputType = getVellumVariablePrimitiveType({
      type: this.nodeData.data.outputType,
      workflowContext: this.workflowContext,
    });

    return [baseStateClassReference, primitiveOutputType];
  }

  protected getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const otherInputs = this.nodeData.inputs.filter(
      (input) => input.id !== this.nodeData.data.templateNodeInputId
    );

    statements.push(
      python.field({
        name: "template",
        initializer: this.getTemplatingInput(),
      })
    );

    statements.push(
      python.field({
        name: "inputs",
        initializer: python.TypeInstantiation.dict(
          otherInputs.map((input) => ({
            key: python.TypeInstantiation.str(input.key),
            value: new NodeInputValuePointer({
              workflowContext: this.workflowContext,
              nodeInputValuePointerData: input.value,
            }),
          }))
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
        name: "output_id",
        initializer: python.TypeInstantiation.uuid(this.nodeData.data.outputId),
      }),
      python.field({
        name: "target_handle_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.targetHandleId
        ),
      }),
      python.field({
        name: "template_input_id",
        initializer: python.TypeInstantiation.uuid(
          this.nodeData.data.templateNodeInputId
        ),
      })
    );

    return statements;
  }

  private getTemplatingInput() {
    const templatingInput = this.nodeData.inputs.find(
      (input) => input.id === this.nodeData.data.templateNodeInputId
    );
    if (!templatingInput) {
      throw new Error("Templating input not found");
    }

    const templateRule = templatingInput.value.rules[0];
    if (!templateRule) {
      throw new Error("Templating input rule not found");
    }

    if (templateRule.type !== "CONSTANT_VALUE") {
      throw new Error("Templating input rule is not a constant value");
    }

    if (templateRule.data.type !== "STRING") {
      throw new Error("Templating input rule is not a string");
    }

    if (!templateRule.data.value) {
      throw new Error(
        "Templating input rule value must be defined and nonempty"
      );
    }

    return python.TypeInstantiation.str(templateRule.data.value);
  }

  protected getErrorOutputId(): string | undefined {
    return this.nodeData.data.errorOutputId;
  }
}
