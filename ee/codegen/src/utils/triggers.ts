import { createPythonClassName, toPythonSafeSnakeCase } from "./casing";

import {
  GENERATED_TRIGGERS_MODULE_NAME,
  VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
} from "src/constants";
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
    case WorkflowTriggerType.MANUAL:
      return {
        className: "ManualTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "manual"],
      };
    case WorkflowTriggerType.SCHEDULED:
      return {
        className: "ScheduleTrigger",
        modulePath: [
          ...workflowContext.modulePath.slice(0, -1),
          GENERATED_TRIGGERS_MODULE_NAME,
          "scheduled",
        ],
      };
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
  }
}
