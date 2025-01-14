import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { NodeTrigger as NodeTriggerType } from "src/types/vellum";

export declare namespace NodeTrigger {
  export interface Args {
    nodeTrigger: NodeTriggerType;
    baseClassRef: python.Reference;
  }
}

export class NodeTrigger extends AstNode {
  private nodeTrigger: NodeTriggerType;
  private baseClassRef: python.Reference;
  private astNode: AstNode;

  public constructor(args: NodeTrigger.Args) {
    super();

    this.nodeTrigger = args.nodeTrigger;
    this.baseClassRef = args.baseClassRef;
    this.astNode = this.constructNodeTrigger();
  }

  private constructNodeTrigger(): AstNode {
    const clazz = python.class_({
      name: "NodeTrigger",
      extends_: [
        python.reference({
          name: this.baseClassRef.name,
          modulePath: this.baseClassRef.modulePath,
          alias: this.baseClassRef.alias,
          attribute: ["Trigger"],
        }),
      ],
    });

    clazz.add(
      python.field({
        name: "merge_behavior",
        initializer: python.TypeInstantiation.str(
          this.nodeTrigger.mergeBehavior
        ),
      })
    );
    return clazz;
  }

  write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
