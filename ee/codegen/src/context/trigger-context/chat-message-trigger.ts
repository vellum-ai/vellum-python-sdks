import { GENERATED_TRIGGERS_MODULE_NAME } from "src/constants";
import { BaseTriggerContext } from "src/context/trigger-context/base";
import { ChatMessageTrigger } from "src/types/vellum";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

export class ChatMessageTriggerContext extends BaseTriggerContext<ChatMessageTrigger> {
  protected getTriggerModuleInfo(): {
    moduleName: string;
    className: string;
    modulePath: string[];
  } {
    const label = this.triggerData.displayData?.label || "chat_message";
    const rawModuleName = toPythonSafeSnakeCase(label);
    let moduleName = rawModuleName;
    let numRenameAttempts = 0;
    while (this.workflowContext.isTriggerModuleNameUsed(moduleName)) {
      moduleName = `${rawModuleName}_${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }
    const className = createPythonClassName(
      this.triggerData.displayData?.label || "ChatMessageTrigger",
      { force: true }
    );

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
