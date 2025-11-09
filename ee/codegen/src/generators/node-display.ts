import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { BaseNodeContext } from "src/context/node-context/base";
import { BASE_NODE_DISPLAY_DEFAULTS } from "src/generators/nodes/display-defaults";
import {
  NodeDisplayData as NodeDisplayDataType,
  WorkflowDataNode,
} from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export declare namespace NodeDisplay {
  export interface Args {
    nodeDisplayData: NodeDisplayDataType | undefined;
    nodeContext: BaseNodeContext<WorkflowDataNode>;
  }
}

export class NodeDisplay extends AstNode {
  private astNode: AstNode | undefined = undefined;

  public constructor(args: NodeDisplay.Args) {
    super();

    const display = this.constructNodeDisplay(
      args.nodeDisplayData,
      args.nodeContext
    );

    if (display) {
      this.astNode = display;
      this.inheritReferences(this.astNode);
    }
  }

  private constructNodeDisplay(
    nodeDisplayData: NodeDisplayDataType | undefined,
    nodeContext: BaseNodeContext<WorkflowDataNode>
  ): AstNode | undefined {
    const baseNodeClassNameAlias =
      nodeContext.baseNodeClassName === nodeContext.nodeClassName
        ? `Base${nodeContext.baseNodeClassName}`
        : undefined;

    const baseDisplayDefaults =
      BASE_NODE_DISPLAY_DEFAULTS[nodeContext.baseNodeClassName] || {};

    const fields: AstNode[] = [];

    if (
      !isNil(nodeDisplayData?.icon) &&
      nodeDisplayData.icon !== baseDisplayDefaults.icon
    ) {
      fields.push(
        python.field({
          name: "icon",
          initializer: python.TypeInstantiation.str(nodeDisplayData.icon),
        })
      );
    }

    if (
      !isNil(nodeDisplayData?.color) &&
      nodeDisplayData.color !== baseDisplayDefaults.color
    ) {
      fields.push(
        python.field({
          name: "color",
          initializer: python.TypeInstantiation.str(nodeDisplayData.color),
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
          name: nodeContext.baseNodeClassName,
          modulePath: nodeContext.baseNodeClassModulePath,
          alias: baseNodeClassNameAlias,
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
