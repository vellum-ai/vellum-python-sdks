import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { WorkflowContext } from "src/context";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { WorkflowTrigger, WorkflowTriggerType } from "src/types/vellum";
import { getTriggerClassInfo } from "src/utils/triggers";

export declare namespace BaseTrigger {
  interface Args {
    trigger: WorkflowTrigger;
    workflowContext: WorkflowContext;
  }
}

export class BaseTrigger {
  public readonly trigger: WorkflowTrigger;
  public readonly workflowContext: WorkflowContext;

  constructor({ trigger, workflowContext }: BaseTrigger.Args) {
    this.trigger = trigger;
    this.workflowContext = workflowContext;
  }

  public generateTriggerClass(): python.Class {
    const triggerInfo = getTriggerClassInfo(this.trigger);

    if (this.trigger.type === WorkflowTriggerType.MANUAL) {
      throw new Error("Manual triggers should not be generated");
    }

    const triggerClass = python.class_({
      name: triggerInfo.className,
      extends_: [
        python.reference({
          name: "IntegrationTrigger",
          modulePath: ["vellum", "workflows", "triggers", "integration"],
        }),
      ],
    });

    if (this.trigger.type === WorkflowTriggerType.INTEGRATION) {
      this.trigger.attributes.forEach((attribute) => {
        triggerClass.add(
          python.field({
            name: attribute.name,
            typeHint: python.Type.str(), // Default to str, could be enhanced
          })
        );
      });

      const configClass = python.class_({
        name: "Config",
        extends_: [
          python.reference({
            name: "IntegrationTrigger",
            modulePath: ["vellum", "workflows", "triggers", "integration"],
            attribute: ["Config"],
          }),
        ],
      });

      configClass.add(
        python.field({
          name: "provider",
          initializer: python.reference({
            name: "VellumIntegrationProviderType",
            modulePath: ["vellum", "workflows", "constants"],
            attribute: [this.trigger.provider || "COMPOSIO"],
          }),
        })
      );

      configClass.add(
        python.field({
          name: "integration_name",
          initializer: python.TypeInstantiation.str(
            this.trigger.integrationName || ""
          ),
        })
      );

      configClass.add(
        python.field({
          name: "slug",
          initializer: python.TypeInstantiation.str(this.trigger.slug || ""),
        })
      );

      triggerClass.add(configClass);
    }

    return triggerClass;
  }

  public getTriggerFile(): TriggerFile {
    return new TriggerFile({ trigger: this });
  }
}

declare namespace TriggerFile {
  interface Args {
    trigger: BaseTrigger;
  }
}

class TriggerFile extends BasePersistedFile {
  private readonly trigger: BaseTrigger;

  constructor({ trigger }: TriggerFile.Args) {
    super({ workflowContext: trigger.workflowContext });
    this.trigger = trigger;
  }

  public getModulePath(): string[] {
    const triggerInfo = getTriggerClassInfo(this.trigger.trigger);
    return [
      ...this.workflowContext.modulePath.slice(0, -1),
      "triggers",
      triggerInfo.className.toLowerCase().replace(/trigger$/, ""),
    ];
  }

  protected getFileStatements(): AstNode[] {
    return [this.trigger.generateTriggerClass()];
  }
}
