import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";

export interface TriggerClassInfo {
  className: string;
  modulePath: string[];
}

export function getTriggerClassInfo(
  triggerType: string
): TriggerClassInfo | null {
  switch (triggerType) {
    case "MANUAL":
      return {
        className: "ManualTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "manual"],
      };
    case "SLACK_MESSAGE":
      return {
        className: "SlackTrigger",
        modulePath: [...VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH, "slack"],
      };
    default:
      return null;
  }
}
