import { python } from "@fern-api/python-ast";
import type { AstNode } from "@fern-api/python-ast/core/AstNode";

import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import type { IntegrationTrigger } from "src/types/vellum";

export declare namespace IntegrationTriggerGenerator {
  interface Args {
    workflowContext: WorkflowContext;
    trigger: IntegrationTrigger;
  }
}

export class IntegrationTriggerGenerator extends BasePersistedFile {
  private readonly trigger: IntegrationTrigger;

  constructor({ workflowContext, trigger }: IntegrationTriggerGenerator.Args) {
    super({ workflowContext });
    this.trigger = trigger;
  }

  getModulePath(): string[] {
    return this.trigger.modulePath;
  }

  getFileStatements(): AstNode[] {
    const triggerClass = python.class_({
      name: this.trigger.className,
      extends_: [
        python.reference({
          name: "IntegrationTrigger",
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
        }),
      ],
    });

    this.trigger.attributes.forEach((attr) => {
      triggerClass.add(
        python.field({
          name: attr.name,
          type: python.Type.str(),
        })
      );
    });

    const configClass = python.class_({
      name: "Config",
      extends_: [
        python.reference({
          name: "IntegrationTrigger",
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
          attribute: ["Config"],
        }),
      ],
    });

    configClass.add(python.codeBlock("pass"));

    triggerClass.add(configClass);

    return [triggerClass];
  }
}
