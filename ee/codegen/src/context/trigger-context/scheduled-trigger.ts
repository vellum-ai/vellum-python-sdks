import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { BaseTriggerContext } from "src/context/trigger-context/base";
import { createPythonClassName } from "src/utils/casing";
import { ScheduledTrigger } from "src/types/vellum";

export class ScheduledTriggerContext extends BaseTriggerContext<ScheduledTrigger> {
  protected getTriggerModuleInfo(): {
    moduleName: string;
    className: string;
    modulePath: string[];
  } {
    const rawModuleName = "scheduled";
    let moduleName = rawModuleName;
    let numRenameAttempts = 0;
    while (this.workflowContext.isTriggerModuleNameUsed(moduleName)) {
      moduleName = `${rawModuleName}_${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }
    const label = this.triggerData.displayData?.label || "ScheduleTrigger";
    const className = createPythonClassName(label, { force: true });

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
