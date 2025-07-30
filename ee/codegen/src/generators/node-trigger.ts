import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { BaseNodeContext } from "src/context/node-context/base";
import {
  NodeTrigger as NodeTriggerType,
  WorkflowDataNode,
} from "src/types/vellum";

export declare namespace NodeTrigger {
  export interface Args {
    nodeTrigger: NodeTriggerType;
    nodeContext: BaseNodeContext<WorkflowDataNode>;
  }
}

export class NodeTrigger extends AstNode {
  private astNode: AstNode | undefined = undefined;

  public constructor(args: NodeTrigger.Args) {
    super();

    const trigger = this.constructNodeTrigger(
      args.nodeTrigger,
      args.nodeContext
    );

    if (trigger) {
      this.astNode = trigger;
      this.inheritReferences(this.astNode);
    }
  }

  private constructNodeTrigger(
    nodeTrigger: NodeTriggerType,
    nodeContext: BaseNodeContext<WorkflowDataNode>
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
        initializer: python.accessAttribute({
          lhs: python.reference({
            name: "MergeBehavior",
            modulePath: [
              ...VELLUM_CLIENT_MODULE_PATH,
              "workflows",
              "types",
              "core",
            ],
          }),
          rhs: python.reference({
            name: nodeTrigger.mergeBehavior,
            modulePath: [],
          }),
        }),
      })
    );
    return clazz;
  }

  write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
