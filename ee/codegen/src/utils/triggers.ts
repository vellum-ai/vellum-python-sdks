import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { WorkflowTrigger, WorkflowTriggerType } from "src/types/vellum";

export interface TriggerClassInfo {
  className: string;
  modulePath: string[];
}

export function getTriggerClassInfo(
  trigger: WorkflowTrigger,
  workflowContext?: WorkflowContext
): TriggerClassInfo {
  switch (trigger.type) {
    case WorkflowTriggerType.MANUAL:
      return {
        className: "ManualTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "manual"],
      };
    case WorkflowTriggerType.INTEGRATION:
      if (workflowContext) {
        return {
          className: trigger.className,
          modulePath: [
            ...workflowContext.modulePath.slice(0, -1),
            "triggers",
            trigger.className.toLowerCase().replace(/trigger$/, ""),
          ],
        };
      }
      return {
        className: trigger.className,
        modulePath: trigger.modulePath,
      };
  }
}
