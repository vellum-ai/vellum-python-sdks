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
      if (workflowContext) {
        return {
          className: "ManualTrigger",
          modulePath: [
            ...workflowContext.modulePath.slice(0, -1),
            "triggers",
            "manual",
          ],
        };
      }
      return {
        className: "ManualTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "manual"],
      };
    case WorkflowTriggerType.INTEGRATION:
      if (workflowContext) {
        const remoteModuleName =
          trigger.modulePath[trigger.modulePath.length - 1];
        if (!remoteModuleName) {
          throw new Error(
            `Integration trigger ${trigger.className} has invalid modulePath`
          );
        }
        return {
          className: trigger.className,
          modulePath: [
            ...workflowContext.modulePath.slice(0, -1),
            "triggers",
            remoteModuleName,
          ],
        };
      }
      return {
        className: trigger.className,
        modulePath: trigger.modulePath,
      };
    case WorkflowTriggerType.SCHEDULED:
      if (workflowContext) {
        return {
          className: "ScheduleTrigger",
          modulePath: [
            ...workflowContext.modulePath.slice(0, -1),
            "triggers",
            "schedule",
          ],
        };
      }
      return {
        className: "ScheduleTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "schedule"],
      };
  }
}
