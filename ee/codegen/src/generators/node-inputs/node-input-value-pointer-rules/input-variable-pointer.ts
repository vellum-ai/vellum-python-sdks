import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { InputVariablePointer } from "src/types/vellum";

export class InputVariablePointerRule extends BaseNodeInputValuePointerRule<InputVariablePointer> {
  getAstNode(): python.AstNode {
    const inputVariablePointerRuleData = this.nodeInputValuePointerRule.data;

    const inputVariableContext =
      this.workflowContext.findInputVariableContextById(
        inputVariablePointerRuleData.inputVariableId
      );

    if (!inputVariableContext) {
      console.warn(
        `Could not find input variable context with id ${inputVariablePointerRuleData.inputVariableId}`
      );
      return python.TypeInstantiation.none();
    }

    return python.reference({
      name: "Inputs",
      modulePath: inputVariableContext.modulePath,
      attribute: [inputVariableContext.name],
    });
  }
}
