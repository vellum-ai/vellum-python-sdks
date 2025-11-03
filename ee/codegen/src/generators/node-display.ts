import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { BaseNodeContext } from "src/context/node-context/base";
import {
  NodeDisplayData as NodeDisplayDataType,
  WorkflowDataNode,
} from "src/types/vellum";

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
    if (isNil(nodeDisplayData?.icon) && isNil(nodeDisplayData?.color)) {
      return undefined;
    }

    const baseNodeClassNameAlias =
      nodeContext.baseNodeClassName === nodeContext.nodeClassName
        ? `Base${nodeContext.baseNodeClassName}`
        : undefined;

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

    if (!isNil(nodeDisplayData?.icon)) {
      clazz.add(
        python.field({
          name: "icon",
          initializer: python.TypeInstantiation.str(nodeDisplayData.icon),
        })
      );
    }

    if (!isNil(nodeDisplayData?.color)) {
      clazz.add(
        python.field({
          name: "color",
          initializer: python.TypeInstantiation.str(nodeDisplayData.color),
        })
      );
    }

    return clazz;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
