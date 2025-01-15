import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeTrigger as NodeTriggerType } from "src/types/vellum";

export declare namespace NodeTrigger {
  export interface Args {
    nodeTrigger: NodeTriggerType;
    nodeContext: GenericNodeContext;
  }
}

export class NodeTrigger extends AstNode {
  private astNode: AstNode;

  public constructor(args: NodeTrigger.Args) {
    super();

    this.astNode = this.constructNodeTrigger(
      args.nodeTrigger,
      args.nodeContext
    );
  }

  private constructNodeTrigger(
    nodeTrigger: NodeTriggerType,
    nodeContext: GenericNodeContext
  ): AstNode {
    const baseNodeClassNameAlias =
      nodeContext.baseNodeClassName === nodeContext.nodeClassName
        ? `Base${nodeContext.baseNodeClassName}`
        : undefined;
    const clazz = python.class_({
      name: "NodeTrigger",
      extends_: [
        python.reference({
          name: nodeContext.baseNodeClassName,
          modulePath: nodeContext.baseNodeClassModulePath,
          alias: baseNodeClassNameAlias,
          attribute: ["Trigger"],
        }),
      ],
    });

    clazz.add(
      python.field({
        name: "merge_behavior",
        initializer: python.TypeInstantiation.str(nodeTrigger.mergeBehavior),
      })
    );
    return clazz;
  }

  write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
