import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { BaseTriggerContext } from "src/context/trigger-context/base";
import { ScheduledTrigger } from "src/types/vellum";

export class ScheduledTriggerContext extends BaseTriggerContext<ScheduledTrigger> {
  protected getTriggerModuleInfo(): {
    moduleName: string;
    className: string;
    modulePath: string[];
  } {
    const moduleName = "scheduled";
    const className = "ScheduleTrigger";

    const modulePath = [
      ...this.workflowContext.modulePath.slice(0, -1),
      GENERATED_TRIGGERS_MODULE_NAME,
      moduleName,
    ];

    return {
      moduleName,
      className,
      modulePath,
    };
  }
}
