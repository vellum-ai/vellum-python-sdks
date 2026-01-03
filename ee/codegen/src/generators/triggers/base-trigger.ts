import {
  GENERATED_TRIGGERS_MODULE_NAME,
  VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
  VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { Class } from "src/generators/extensions/class";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { Field } from "src/generators/extensions/field";
import { FloatInstantiation } from "src/generators/extensions/float-instantiation";
import { IntInstantiation } from "src/generators/extensions/int-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { StrType } from "src/generators/extensions/str-type";
import { isNilOrEmpty } from "src/utils/typing";

import type { AstNode } from "src/generators/extensions/ast-node";
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
    const displayData = this.trigger.displayData;

    if (!displayData) {
      return undefined;
    }

    const fields: AstNode[] = [];

    fields.push(
      new Field({
        name: "label",
        initializer: new StrInstantiation(displayData.label),
      })
    );

    if (displayData.position != null) {
      fields.push(
        new Field({
          name: "x",
          initializer: new FloatInstantiation(displayData.position.x),
        })
      );
      fields.push(
        new Field({
          name: "y",
          initializer: new FloatInstantiation(displayData.position.y),
        })
      );
    }

    if (displayData.z_index != null) {
      fields.push(
        new Field({
          name: "z_index",
          initializer: new IntInstantiation(displayData.z_index),
        })
      );
    }

    if (displayData.icon != null) {
      fields.push(
        new Field({
          name: "icon",
          initializer: new StrInstantiation(displayData.icon),
        })
      );
    }

    if (displayData.color != null) {
      fields.push(
        new Field({
          name: "color",
          initializer: new StrInstantiation(displayData.color),
        })
      );
    }

    if (displayData.comment != null) {
      const commentArgs: MethodArgument[] = [];
      const { expanded, value } = displayData.comment;

      if (expanded) {
        commentArgs.push(
          new MethodArgument({
            name: "expanded",
            value: new BoolInstantiation(expanded),
          })
        );
      }

      if (value) {
        commentArgs.push(
          new MethodArgument({
            name: "value",
            value: new StrInstantiation(value),
          })
        );
      }

      if (isNilOrEmpty(commentArgs)) {
        return undefined;
      }

      fields.push(
        new Field({
          name: "comment",
          initializer: new ClassInstantiation({
            classReference: new Reference({
              name: "NodeDisplayComment",
              modulePath: VELLUM_WORKFLOW_EDITOR_TYPES_PATH,
            }),
            arguments_: commentArgs,
          }),
        })
      );
    }

    if (fields.length === 0) {
      return undefined;
    }

    const displayClass = new Class({
      name: "Display",
      extends_: [
        new Reference({
          name: this.getBaseTriggerClassName(),
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
          attribute: ["Display"],
        }),
      ],
    });

    fields.forEach((field) => displayClass.add(field));

    return displayClass;
  }

  getModulePath(): string[] {
    // Prefer the module name resolved by the trigger context (ensures deduplication)
    const triggerContext = this.workflowContext.findTriggerContext(
      this.trigger.id
    );
    const moduleNameFromContext =
      triggerContext?.triggerModuleName ?? this.getModuleName();
    return [
      ...this.workflowContext.modulePath.slice(0, -1),
      GENERATED_TRIGGERS_MODULE_NAME,
      moduleNameFromContext,
    ];
  }

  getFileStatements(): AstNode[] {
    const triggerClass = new Class({
      name: this.className,
      extends_: [
        new Reference({
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
    return this.trigger.attributes.map(
      (attr) =>
        new Field({
          name: attr.key,
          type: new StrType(),
        })
    );
  }
}
