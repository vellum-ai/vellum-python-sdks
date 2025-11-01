import { python } from "@fern-api/python-ast";

import {
  GENERATED_TRIGGERS_MODULE_NAME,
  VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
} from "src/constants";
import { WorkflowContext } from "src/context";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { createPythonClassName } from "src/utils/casing";

import type { AstNode } from "@fern-api/python-ast/core/AstNode";
import type { IntegrationTrigger } from "src/types/vellum";

export declare namespace IntegrationTriggerGenerator {
  interface Args {
    workflowContext: WorkflowContext;
    trigger: IntegrationTrigger;
  }
}

export class IntegrationTriggerGenerator extends BasePersistedFile {
  private readonly trigger: IntegrationTrigger;
  private readonly className: string;

  constructor({ workflowContext, trigger }: IntegrationTriggerGenerator.Args) {
    super({ workflowContext });
    this.trigger = trigger;
    this.className = createPythonClassName(this.trigger.execConfig.slug, {
      force: true,
    });
  }

  getModulePath(): string[] {
    return [
      ...this.workflowContext.modulePath.slice(0, -1),
      GENERATED_TRIGGERS_MODULE_NAME,
      this.trigger.execConfig.slug.toLowerCase(),
    ];
  }

  getFileStatements(): AstNode[] {
    const triggerClass = python.class_({
      name: this.className,
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

    configClass.add(
      python.field({
        name: "type",
        initializer: python.TypeInstantiation.str(this.trigger.execConfig.type),
      })
    );
    configClass.add(
      python.field({
        name: "integration_name",
        initializer: python.TypeInstantiation.str(
          this.trigger.execConfig.integrationName
        ),
      })
    );
    configClass.add(
      python.field({
        name: "slug",
        initializer: python.TypeInstantiation.str(this.trigger.execConfig.slug),
      })
    );
    if (this.trigger.execConfig.setupAttributes.length > 0) {
      configClass.add(
        python.field({
          name: "setupAttributes",
          initializer: python.TypeInstantiation.dict(
            this.trigger.execConfig.setupAttributes.map((attr) => ({
              key: python.TypeInstantiation.str(attr.key),
              value:
                typeof attr.default?.value === "string"
                  ? python.TypeInstantiation.str(attr.default.value)
                  : python.TypeInstantiation.none(),
            }))
          ),
        })
      );
    }

    triggerClass.add(configClass);

    return [triggerClass];
  }
}
