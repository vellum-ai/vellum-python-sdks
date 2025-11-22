import { python } from "@fern-api/python-ast";

import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { Class } from "src/generators/extensions/class";
import { BaseTrigger } from "src/generators/triggers/base-trigger";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

import type { AstNode } from "@fern-api/python-ast/core/AstNode";
import type { ScheduledTrigger as ScheduledTriggerType } from "src/types/vellum";

export declare namespace ScheduledTrigger {
  interface Args {
    workflowContext: BaseTrigger.Args<ScheduledTriggerType>["workflowContext"];
    trigger: ScheduledTriggerType;
  }
}

export class ScheduledTrigger extends BaseTrigger<ScheduledTriggerType> {
  protected generateClassName(): string {
    const label = this.trigger.displayData?.label || "ScheduleTrigger";
    return createPythonClassName(label, {
      force: true,
    });
  }

  protected getModuleName(): string {
    const label = this.trigger.displayData?.label || "scheduled";
    return toPythonSafeSnakeCase(label);
  }

  protected getBaseTriggerClassName(): string {
    return "ScheduleTrigger";
  }

  protected getTriggerClassBody(): AstNode[] {
    const body: AstNode[] = [];

    body.push(this.createConfigClass());

    return body;
  }

  private createConfigClass(): AstNode {
    const configClass = new Class({
      name: "Config",
      extends_: [
        python.reference({
          name: "ScheduleTrigger",
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
          attribute: ["Config"],
        }),
      ],
    });

    configClass.add(
      python.field({
        name: "cron",
        initializer: python.TypeInstantiation.str(this.trigger.cron),
      })
    );

    configClass.add(
      python.field({
        name: "timezone",
        initializer: this.trigger.timezone
          ? python.TypeInstantiation.str(this.trigger.timezone)
          : python.TypeInstantiation.none(),
      })
    );

    return configClass;
  }
}
