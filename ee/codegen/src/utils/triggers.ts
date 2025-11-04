import { createPythonClassName } from "./casing";

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
          trigger.execConfig.slug.toLowerCase(),
        ],
      };
  }
}
