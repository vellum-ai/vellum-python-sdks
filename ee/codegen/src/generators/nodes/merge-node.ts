import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { MergeNodeContext } from "src/context/node-context/merge-node";
import { BaseNode } from "src/generators/nodes/bases/base";
import { MergeNode as MergeNodeType } from "src/types/vellum";

export class MergeNode extends BaseNode<MergeNodeType, MergeNodeContext> {
  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const mergeStrategyRef = python.reference({
      name: "MergeBehavior",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
        "types",
      ],
      attribute: [this.nodeData.data.mergeStrategy],
    });

    const baseClass = this.getNodeBaseClass();

    const triggerClass = python.class_({
      name: "Trigger",
      extends_: [
        python.reference({
          name: baseClass.name,
          modulePath: baseClass.modulePath,
          alias: baseClass.alias,
          attribute: ["Trigger"],
        }),
      ],
    });
    triggerClass.add(
      python.field({
        name: "merge_behavior",
        initializer: mergeStrategyRef,
      })
    );

    statements.push(triggerClass);

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const targetHandleIds = python.TypeInstantiation.list(
      this.nodeData.data.targetHandles.map((targetHandle) =>
        python.TypeInstantiation.uuid(targetHandle.id)
      )
    );
    statements.push(
      python.field({ name: "target_handle_ids", initializer: targetHandleIds })
    );

    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    return undefined;
  }

  getErrorOutputId(): string | undefined {
    return undefined;
  }
}
