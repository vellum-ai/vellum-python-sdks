import { VELLUM_CLIENT_MODULE_PATH } from "src/constants";
import { BaseNodeContext } from "src/context/node-context/base";
import { AccessAttribute } from "src/generators/extensions/access-attribute";
import { AstNode } from "src/generators/extensions/ast-node";
import { Class } from "src/generators/extensions/class";
import { Field } from "src/generators/extensions/field";
import { Reference } from "src/generators/extensions/reference";
import { Writer } from "src/generators/extensions/writer";
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
    const clazz = new Class({
      name: "Trigger",
      extends_: [
        new Reference({
          name: nodeContext.baseNodeClassName,
          modulePath: nodeContext.baseNodeClassModulePath,
          alias: baseNodeClassNameAlias,
          attribute: ["Trigger"],
        }),
      ],
    });

    clazz.add(
      new Field({
        name: "merge_behavior",
        initializer: new AccessAttribute({
          lhs: new Reference({
            name: "MergeBehavior",
            modulePath: [
              ...VELLUM_CLIENT_MODULE_PATH,
              "workflows",
              "types",
              "core",
            ],
          }),
          rhs: new Reference({
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
