import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { WorkflowTrigger } from "src/types/vellum";

export interface TriggerClassInfo {
  className: string;
  modulePath: string[];
}

export function getTriggerClassInfo(
  trigger: WorkflowTrigger
): TriggerClassInfo | null {
  switch (trigger.type) {
    case "MANUAL":
      return {
        className: "ManualTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "manual"],
      };
    case "INTEGRATION":
      // For INTEGRATION triggers, class_name and module_path are required from serialization
      if (!trigger.class_name || !trigger.module_path) {
        return null;
      }
      return {
        className: trigger.class_name,
        modulePath: trigger.module_path,
      };
    default:
      return null;
  }
}
