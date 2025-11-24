import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { NodeInputNotFoundError } from "src/generators/errors";
import { TriggerAttributePointer } from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

export class TriggerAttributePointerRule extends BaseNodeInputValuePointerRule<TriggerAttributePointer> {
  getAstNode(): python.AstNode {
    const triggerAttributePointerRuleData = this.nodeInputValuePointerRule.data;

    // Find the trigger in the workflow context
    const trigger = this.workflowContext.triggers?.find(
      (t) => t.id === triggerAttributePointerRuleData.triggerId
    );

    if (!trigger) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find trigger with id ${triggerAttributePointerRuleData.triggerId}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }

    // Find the attribute name from the trigger's attributes
    const attribute = trigger.attributes.find(
      (attr) => attr.id === triggerAttributePointerRuleData.attributeId
    );

    if (!attribute) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find attribute with id ${triggerAttributePointerRuleData.attributeId} in trigger ${triggerAttributePointerRuleData.triggerId}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }

    // Get the trigger class information based on trigger
    const triggerClassInfo = getTriggerClassInfo(trigger, this.workflowContext);
    if (!triggerClassInfo) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not get trigger class info for trigger ${triggerAttributePointerRuleData.triggerId}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }

    // Generate: TriggerClassName.attributeName
    return python.reference({
      name: triggerClassInfo.className,
      modulePath: triggerClassInfo.modulePath,
      attribute: [attribute.key],
    });
  }
}
