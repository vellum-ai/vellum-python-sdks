import { createPythonClassName, toPythonSafeSnakeCase } from "./casing";

import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { WorkflowContext } from "src/context/workflow-context/workflow-context";
import { WorkflowTrigger, WorkflowTriggerType } from "src/types/vellum";

export interface TriggerClassInfo {
  className: string;
  modulePath: string[];
}

export function getTriggerClassInfo(
  trigger: WorkflowTrigger,
  workflowContext: WorkflowContext
): TriggerClassInfo {
  // If a trigger context exists for this trigger, use it as the source of truth
  const triggerContext = workflowContext.findTriggerContext(trigger.id);
  if (triggerContext) {
    return {
      className: triggerContext.triggerClassName,
      modulePath: triggerContext.triggerModulePath,
    };
  }

  switch (trigger.type) {
    case WorkflowTriggerType.MANUAL: {
      const label = trigger.displayData?.label || "ManualTrigger";
      return {
        className: createPythonClassName(label, { force: true }),
        modulePath: [
          ...workflowContext.modulePath.slice(0, -1),
          GENERATED_TRIGGERS_MODULE_NAME,
          toPythonSafeSnakeCase(trigger.displayData?.label || "manual"),
        ],
      };
    }
    case WorkflowTriggerType.SCHEDULED: {
      const label = trigger.displayData?.label || "ScheduleTrigger";
      return {
        className: createPythonClassName(label, { force: true }),
        modulePath: [
          ...workflowContext.modulePath.slice(0, -1),
          GENERATED_TRIGGERS_MODULE_NAME,
          toPythonSafeSnakeCase(trigger.displayData?.label || "scheduled"),
        ],
      };
    }
    case WorkflowTriggerType.INTEGRATION:
      return {
        className: createPythonClassName(trigger.execConfig.slug, {
          force: true,
        }),
        modulePath: [
          ...workflowContext.modulePath.slice(0, -1),
          GENERATED_TRIGGERS_MODULE_NAME,
          toPythonSafeSnakeCase(trigger.execConfig.slug),
        ],
      };
    case WorkflowTriggerType.CHAT_MESSAGE: {
      const label = trigger.displayData?.label || "ChatMessageTrigger";
      return {
        className: createPythonClassName(label, { force: true }),
        modulePath: [
          ...workflowContext.modulePath.slice(0, -1),
          GENERATED_TRIGGERS_MODULE_NAME,
          toPythonSafeSnakeCase(trigger.displayData?.label || "chat_message"),
        ],
      };
    }
  }
}
