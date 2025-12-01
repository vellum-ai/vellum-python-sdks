import { BaseNodeInputValuePointerRule } from "./base";

import { NodeInputNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { InputVariablePointer } from "src/types/vellum";

export class InputVariablePointerRule extends BaseNodeInputValuePointerRule<InputVariablePointer> {
  getAstNode(): AstNode {
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
      return new NoneInstantiation();
    }

    return new Reference({
      name: inputVariableContext.definition.name,
      modulePath: inputVariableContext.definition.module,
      attribute: [inputVariableContext.name],
    });
  }
}
