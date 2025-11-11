import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { BaseTriggerContext } from "src/context/trigger-context/base";
import { IntegrationTrigger } from "src/types/vellum";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

export class IntegrationTriggerContext extends BaseTriggerContext<IntegrationTrigger> {
  protected getTriggerModuleInfo(): {
    moduleName: string;
    className: string;
    modulePath: string[];
  } {
    const slug = this.triggerData.execConfig.slug;
    const rawModuleName = toPythonSafeSnakeCase(slug);
    // Deduplicate trigger module names within a workflow
    let moduleName = rawModuleName;
    let numRenameAttempts = 0;
    while (this.workflowContext.isTriggerModuleNameUsed(moduleName)) {
      moduleName = `${rawModuleName}_${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }
    const label = this.triggerData.displayData?.label || "IntegrationTrigger";
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
