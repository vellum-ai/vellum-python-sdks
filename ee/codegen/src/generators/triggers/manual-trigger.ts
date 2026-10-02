import { BaseTrigger } from "src/generators/triggers/base-trigger";
import { createPythonClassName, toPythonSafeSnakeCase } from "src/utils/casing";

import type { AstNode } from "src/generators/extensions/ast-node";
import type { ManualTrigger as ManualTriggerType } from "src/types/vellum";

export declare namespace ManualTriggerGenerator {
  interface Args {
    workflowContext: BaseTrigger.Args<ManualTriggerType>["workflowContext"];
    trigger: ManualTriggerType;
  }
}

export class ManualTrigger extends BaseTrigger<ManualTriggerType> {
  protected generateClassName(): string {
    const label = this.trigger.displayData?.label || "ManualTrigger";
    return createPythonClassName(label, {
      force: true,
    });
  }

  protected getModuleName(): string {
    const label = this.trigger.displayData?.label || "manual";
    return toPythonSafeSnakeCase(label);
  }

  protected getBaseTriggerClassName(): string {
    return "ManualTrigger";
  }

  protected getTriggerClassBody(): AstNode[] {
    const body: AstNode[] = [];

    // Add attribute fields if any
    body.push(...this.createAttributeFields());

    return body;
  }
}
