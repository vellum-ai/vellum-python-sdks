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
    const triggerInfo = getTriggerClassInfo(this.trigger, this.workflowContext);

    switch (this.trigger.type) {
      case WorkflowTriggerType.MANUAL: {
        const triggerClass = python.class_({
          name: triggerInfo.className,
          extends_: [
            python.reference({
              name: "_ManualTrigger",
            }),
          ],
        });
        return triggerClass;
      }
      case WorkflowTriggerType.INTEGRATION: {
        const triggerClass = python.class_({
          name: triggerInfo.className,
          extends_: [
            python.reference({
              name: `_${triggerInfo.className}`,
            }),
          ],
        });
        return triggerClass;
      }
      case WorkflowTriggerType.SCHEDULED: {
        const triggerClass = python.class_({
          name: triggerInfo.className,
          extends_: [
            python.reference({
              name: "_ScheduleTrigger",
            }),
          ],
        });
        return triggerClass;
      }
    }
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
    const triggerInfo = getTriggerClassInfo(
      this.trigger.trigger,
      this.workflowContext
    );
    return triggerInfo.modulePath;
  }

  protected getFileStatements(): AstNode[] {
    const triggerClass = this.trigger.generateTriggerClass();

    switch (this.trigger.trigger.type) {
      case WorkflowTriggerType.MANUAL: {
        this.addReference(
          python.reference({
            name: "ManualTrigger",
            alias: "_ManualTrigger",
            modulePath: ["vellum", "workflows", "triggers", "manual"],
          })
        );
        break;
      }
      case WorkflowTriggerType.INTEGRATION: {
        const remoteTriggerInfo = getTriggerClassInfo(this.trigger.trigger);
        const triggerInfo = getTriggerClassInfo(
          this.trigger.trigger,
          this.workflowContext
        );
        this.addReference(
          python.reference({
            name: triggerInfo.className,
            alias: `_${triggerInfo.className}`,
            modulePath: remoteTriggerInfo.modulePath,
          })
        );
        break;
      }
      case WorkflowTriggerType.SCHEDULED: {
        this.addReference(
          python.reference({
            name: "ScheduleTrigger",
            alias: "_ScheduleTrigger",
            modulePath: ["vellum", "workflows", "triggers", "schedule"],
          })
        );
        break;
      }
    }

    return [triggerClass];
  }
}
