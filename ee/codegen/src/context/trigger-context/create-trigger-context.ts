import { WorkflowContext } from "src/context";
import { ChatMessageTriggerContext } from "src/context/trigger-context/chat-message-trigger";
import { IntegrationTriggerContext } from "src/context/trigger-context/integration-trigger";
import { ScheduledTriggerContext } from "src/context/trigger-context/scheduled-trigger";
import {
  ChatMessageTrigger,
  IntegrationTrigger,
  ScheduledTrigger,
  WorkflowTrigger,
} from "src/types/vellum";

export declare namespace createTriggerContext {
  interface Args {
    workflowContext: WorkflowContext;
    triggerData: WorkflowTrigger;
  }
}

export function createTriggerContext({
  workflowContext,
  triggerData,
}: createTriggerContext.Args): void {
  const triggerType = triggerData.type;

  switch (triggerType) {
    case "INTEGRATION": {
      const triggerContext = new IntegrationTriggerContext({
        workflowContext,
        triggerData: triggerData as IntegrationTrigger,
      });
      workflowContext.addTriggerContext(triggerContext);
      break;
    }
    case "SCHEDULED": {
      const triggerContext = new ScheduledTriggerContext({
        workflowContext,
        triggerData: triggerData as ScheduledTrigger,
      });
      workflowContext.addTriggerContext(triggerContext);
      break;
    }
    case "CHAT_MESSAGE": {
      const triggerContext = new ChatMessageTriggerContext({
        workflowContext,
        triggerData: triggerData as ChatMessageTrigger,
      });
      workflowContext.addTriggerContext(triggerContext);
      break;
    }
    case "MANUAL":
      // For now, we don't create contexts for MANUAL triggers
      // as they don't have associated files
      break;
    default:
      // Unknown trigger type, skip
      break;
  }
}
