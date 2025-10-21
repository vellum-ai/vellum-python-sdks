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
      // TypeScript guarantees className and modulePath exist for INTEGRATION triggers
      return {
        className: trigger.className,
        modulePath: trigger.modulePath,
      };
  }
}
