import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeOutputs } from "src/generators/node-outputs";
import { NodeTrigger } from "src/generators/node-trigger";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { GenericNode as GenericNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

export class GenericNode extends BaseSingleFileNode<
  GenericNodeType,
  GenericNodeContext
> {
  getNodeDecorators(): python.Decorator[] | undefined {
    if (!this.nodeData.adornments) {
      return [];
    }
    return this.nodeData.adornments.map((adornment) =>
      python.decorator({
        callable: python.invokeMethod({
          methodReference: python.reference({
            name: adornment.base.name,
            attribute: ["wrap"],
            modulePath: adornment.base.module,
          }),
          arguments_: adornment.attributes.map((attr) =>
            python.methodArgument({
              name: attr.name,
              value: new WorkflowValueDescriptor({
                workflowValueDescriptor: attr.value,
                nodeContext: this.nodeContext,
                workflowContext: this.workflowContext,
                iterableConfig: { endWithComma: false },
              }),
            })
          ),
        }),
      })
    );
  }

  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    this.nodeData.attributes.forEach((attribute) => {
      statements.push(
        python.field({
          name: toPythonSafeSnakeCase(attribute.name),
          initializer: new WorkflowValueDescriptor({
            nodeContext: this.nodeContext,
            workflowValueDescriptor: attribute.value,
            workflowContext: this.workflowContext,
          }),
        })
      );
    });

    if (this.nodeData.trigger.mergeBehavior !== "AWAIT_ATTRIBUTES") {
      statements.push(
        new NodeTrigger({
          nodeTrigger: this.nodeData.trigger,
          nodeContext: this.nodeContext,
        })
      );
    }

    if (this.nodeData.outputs.length > 0) {
      statements.push(
        new NodeOutputs({
          nodeOutputs: this.nodeData.outputs,
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
        })
      );
    }

    return statements;
  }

  getNodeDisplayClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    return statements;
  }

  protected getOutputDisplay(): Field | undefined {
    return undefined;
  }

  protected getErrorOutputId(): string | undefined {
    return undefined;
  }

  private getModulePath(): string[] {
    return this.nodeContext.nodeModulePath;
  }

  public async persist(): Promise<void> {
    const modulePath = this.getModulePath();
    const fileName = modulePath[modulePath.length - 1] + ".py";

    const relativePath = `nodes/${fileName}`;

    this.workflowContext.addPythonCodeMergeableNodeFile(relativePath);

    await super.persist();
  }
}
