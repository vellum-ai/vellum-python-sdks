import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH } from "src/constants";
import {
  TriggerDisplayData as TriggerDisplayDataType,
} from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export declare namespace TriggerDisplay {
  export interface Args {
    triggerDisplayData: TriggerDisplayDataType | undefined;
    baseTriggerClassName: string;
  }
}

export class TriggerDisplay extends AstNode {
  private astNode: AstNode | undefined = undefined;

  public constructor(args: TriggerDisplay.Args) {
    super();

    const display = this.constructTriggerDisplay(
      args.triggerDisplayData,
      args.baseTriggerClassName
    );

    if (display) {
      this.astNode = display;
      this.inheritReferences(this.astNode);
    }
  }

  private constructTriggerDisplay(
    triggerDisplayData: TriggerDisplayDataType | undefined,
    baseTriggerClassName: string
  ): AstNode | undefined {
    const fields: AstNode[] = [];

    if (!isNil(triggerDisplayData?.icon)) {
      fields.push(
        python.field({
          name: "icon",
          initializer: python.TypeInstantiation.str(triggerDisplayData.icon),
        })
      );
    }

    if (!isNil(triggerDisplayData?.color)) {
      fields.push(
        python.field({
          name: "color",
          initializer: python.TypeInstantiation.str(triggerDisplayData.color),
        })
      );
    }

    if (isNilOrEmpty(fields)) {
      return undefined;
    }

    const clazz = python.class_({
      name: "Display",
      extends_: [
        python.reference({
          name: baseTriggerClassName,
          modulePath: VELLUM_WORKFLOW_TRIGGERS_MODULE_PATH,
          attribute: ["Display"],
        }),
      ],
    });

    fields.forEach((field) => clazz.add(field));

    return clazz;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
