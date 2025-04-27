import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { NodeInputNotFoundError } from "src/generators/errors";
import { InputVariablePointer } from "src/types/vellum";

export class InputVariablePointerRule extends BaseNodeInputValuePointerRule<InputVariablePointer> {
  getAstNode(): python.AstNode {
    const inputVariablePointerRuleData = this.nodeInputValuePointerRule.data;

    const inputVariableContext =
      this.workflowContext.findInputVariableContextById(
        inputVariablePointerRuleData.inputVariableId
      );

    if (!inputVariableContext) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find input variable context with id ${inputVariablePointerRuleData.inputVariableId}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }

    return python.reference({
      name: inputVariableContext.definition.name,
      modulePath: inputVariableContext.definition.module,
      attribute: [inputVariableContext.name],
    });
  }
}
