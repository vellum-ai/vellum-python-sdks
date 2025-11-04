import { python } from "@fern-api/python-ast";

import { BaseTrigger } from "src/generators/triggers/base-trigger";

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
    return "ScheduleTrigger";
  }

  protected getModuleName(): string {
    return "scheduled";
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
    const configClass = python.class_({
      name: "Config",
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

  protected getClassDocstring(): string | undefined {
    return `Trigger representing time-based workflow invocation.
Supports Cron-based schedules (e.g., "0 9 * * MON" for every Monday at 9am)`;
  }
}
