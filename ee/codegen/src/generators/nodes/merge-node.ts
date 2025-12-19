import { MergeNodeContext } from "src/context/node-context/merge-node";
import { AstNode } from "src/generators/extensions/ast-node";
import { Class } from "src/generators/extensions/class";
import { Field } from "src/generators/extensions/field";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { BaseNode } from "src/generators/nodes/bases/base";
import { MergeNode as MergeNodeType } from "src/types/vellum";

export class MergeNode extends BaseNode<MergeNodeType, MergeNodeContext> {
  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const mergeStrategyRef = new Reference({
      name: "MergeBehavior",
      modulePath: [
        ...this.workflowContext.sdkModulePathNames.WORKFLOWS_MODULE_PATH,
        "types",
      ],
      attribute: [this.nodeData.data.mergeStrategy],
    });

    const baseClass = this.getNodeBaseClass();

    const triggerClass = new Class({
      name: "Trigger",
      extends_: [
        new Reference({
          name: baseClass.name,
          modulePath: baseClass.modulePath,
          alias: baseClass.alias,
          attribute: ["Trigger"],
        }),
      ],
    });
    triggerClass.add(
      new Field({
        name: "merge_behavior",
        initializer: mergeStrategyRef,
      })
    );

    statements.push(triggerClass);

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];

    const targetHandleIds = new ListInstantiation(
      this.nodeData.data.targetHandles.map(
        (targetHandle) => new UuidInstantiation(targetHandle.id)
      )
    );
    statements.push(
      new Field({ name: "target_handle_ids", initializer: targetHandleIds })
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
