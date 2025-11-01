import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { BaseTriggerContext } from "src/context/trigger-context/base";
import { IntegrationTrigger } from "src/types/vellum";
import { createPythonClassName } from "src/utils/casing";

export class IntegrationTriggerContext extends BaseTriggerContext<IntegrationTrigger> {
  protected getTriggerModuleInfo(): {
    moduleName: string;
    className: string;
    modulePath: string[];
  } {
    const slug = this.triggerData.execConfig.slug;
    const moduleName = slug.toLowerCase();
    const className = createPythonClassName(slug, { force: true });

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
