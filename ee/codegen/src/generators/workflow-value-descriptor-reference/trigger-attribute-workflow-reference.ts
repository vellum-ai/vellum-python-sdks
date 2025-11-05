import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { TriggerAttributeWorkflowReference as TriggerAttributeWorkflowReferenceType } from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

export class TriggerAttributeWorkflowReference extends BaseNodeInputWorkflowReference<TriggerAttributeWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const triggerAttributePointer = this.nodeInputWorkflowReferencePointer;

    // Find the trigger in the workflow context
    const trigger = this.workflowContext.triggers?.find(
      (t) => t.id === triggerAttributePointer.triggerId
    );

    if (!trigger) {
      return undefined;
    }

    // Find the attribute name from the trigger's attributes
    const attribute = trigger.attributes.find(
      (attr) => attr.id === triggerAttributePointer.attributeId
    );

    if (!attribute) {
      return undefined;
    }

    // Get the trigger class information based on trigger
    const triggerClassInfo = getTriggerClassInfo(trigger, this.workflowContext);
    if (!triggerClassInfo) {
      return undefined;
    }

    // Generate: TriggerClassName.attributeName
    return python.reference({
      name: triggerClassInfo.className,
      modulePath: triggerClassInfo.modulePath,
      attribute: [attribute.key],
    });
  }
}
