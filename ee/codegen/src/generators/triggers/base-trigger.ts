import { python } from "@fern-api/python-ast";

import {
  GENERATED_TRIGGERS_MODULE_NAME,
  VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { TriggerDisplay } from "src/generators/trigger-display";

import type { AstNode } from "@fern-api/python-ast/core/AstNode";
import type { WorkflowTrigger } from "src/types/vellum";

export declare namespace BaseTrigger {
  interface Args<T extends WorkflowTrigger> {
    workflowContext: WorkflowContext;
    trigger: T;
  }
}

export abstract class BaseTrigger<
  T extends WorkflowTrigger
> extends BasePersistedFile {
  protected readonly trigger: T;
  protected readonly className: string;

  constructor({ workflowContext, trigger }: BaseTrigger.Args<T>) {
    super({ workflowContext });
    this.trigger = trigger;
    this.className = this.generateClassName();
  }

  /**
   * Generate the Python class name for this trigger.
   * Override this method to customize class name generation.
   */
  protected abstract generateClassName(): string;

  /**
   * Get the module name for this trigger (e.g., "integration_trigger", "scheduled").
   * This is used as part of the module path and should be lowercase.
   */
  protected abstract getModuleName(): string;

  /**
   * Get the name of the base trigger class to extend from (e.g., "IntegrationTrigger").
   */
  protected abstract getBaseTriggerClassName(): string;

  /**
   * Generate the statements for the trigger class body (fields, nested classes, etc.).
   */
  protected abstract getTriggerClassBody(): AstNode[];

  /**
   * Optionally create a Display class for this trigger.
   * Override this method to provide a custom Display class.
   * @returns The Display class AstNode, or undefined if no Display class is needed
   */
  protected createDisplayClass(): AstNode | undefined {
    if (this.trigger.displayData) {
      return new TriggerDisplay({
        triggerDisplayData: this.trigger.displayData,
        baseTriggerClassName: this.getBaseTriggerClassName(),
      });
    }

    return undefined;
  }

  getModulePath(): string[] {
    return [
      ...this.workflowContext.modulePath.slice(0, -1),
      GENERATED_TRIGGERS_MODULE_NAME,
      this.getModuleName(),
    ];
  }

  getFileStatements(): AstNode[] {
    const triggerClass = python.class_({
      name: this.className,
      extends_: [
        python.reference({
          name: this.getBaseTriggerClassName(),
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
        }),
      ],
    });

    // Add the trigger-specific class body
    const classBody = this.getTriggerClassBody();
    classBody.forEach((node) => triggerClass.add(node));

    // Add the Display class as a nested class if defined
    const displayClass = this.createDisplayClass();
    if (displayClass) {
      triggerClass.add(displayClass);
    }

    return [triggerClass];
  }

  /**
   * Helper method to create fields from trigger attributes.
   * All triggers have attributes, so this is a common helper.
   */
  protected createAttributeFields(): AstNode[] {
    return this.trigger.attributes.map((attr) =>
      python.field({
        name: attr.name,
        type: python.Type.str(),
      })
    );
  }
}
