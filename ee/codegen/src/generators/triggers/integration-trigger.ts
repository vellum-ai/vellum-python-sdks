import { python } from "@fern-api/python-ast";

import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import { BaseTrigger } from "src/generators/triggers/base-trigger";
import { createPythonClassName } from "src/utils/casing";

import type { AstNode } from "@fern-api/python-ast/core/AstNode";
import type { IntegrationTrigger as IntegrationTriggerType } from "src/types/vellum";

export declare namespace IntegrationTriggerGenerator {
  interface Args {
    workflowContext: BaseTrigger.Args<IntegrationTriggerType>["workflowContext"];
    trigger: IntegrationTriggerType;
  }
}

export class IntegrationTrigger extends BaseTrigger<IntegrationTriggerType> {
  protected generateClassName(): string {
    return createPythonClassName(this.trigger.execConfig.slug, {
      force: true,
    });
  }

  protected getModuleName(): string {
    return this.trigger.execConfig.slug.toLowerCase();
  }

  protected getBaseTriggerClassName(): string {
    return "IntegrationTrigger";
  }

  protected getTriggerClassBody(): AstNode[] {
    const body: AstNode[] = [];

    // Add attribute fields
    body.push(...this.createAttributeFields());

    // Create Config class
    const configFields: AstNode[] = [];

    configFields.push(
      python.field({
        name: "type",
        initializer: python.TypeInstantiation.str(this.trigger.execConfig.type),
      })
    );

    configFields.push(
      python.field({
        name: "integration_name",
        initializer: python.TypeInstantiation.str(
          this.trigger.execConfig.integrationName
        ),
      })
    );

    configFields.push(
      python.field({
        name: "slug",
        initializer: python.TypeInstantiation.str(this.trigger.execConfig.slug),
      })
    );

    if (this.trigger.execConfig.setupAttributes.length > 0) {
      configFields.push(
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

    body.push(this.createConfigClass(configFields));

    return body;
  }

  /**
   * Helper method to create a Config class that extends from IntegrationTrigger's Config.
   * This is specific to IntegrationTrigger.
   */
  private createConfigClass(configFields: AstNode[]): AstNode {
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

    configFields.forEach((field) => configClass.add(field));

    return configClass;
  }
}
