import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { WorkflowTrigger, WorkflowTriggerType } from "src/types/vellum";

export interface TriggerClassInfo {
  className: string;
  modulePath: string[];
}

export function getTriggerClassInfo(
  trigger: WorkflowTrigger
): TriggerClassInfo {
  switch (trigger.type) {
    case WorkflowTriggerType.MANUAL:
      return {
        className: "ManualTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "manual"],
      };
    case WorkflowTriggerType.INTEGRATION:
      // TypeScript guarantees class_name and module_path exist for INTEGRATION triggers
      return {
        className: trigger.class_name,
        modulePath: trigger.module_path,
      };
  }
}
