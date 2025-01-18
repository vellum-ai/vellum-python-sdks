import { python } from "@fern-api/python-ast";
import { Field } from "@fern-api/python-ast/Field";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeOutput } from "src/generators/node-output";
import { NodePorts } from "src/generators/node-port";
import { NodeTrigger } from "src/generators/node-trigger";
import { BaseSingleFileNode } from "src/generators/nodes/bases/single-file-base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { GenericNode as GenericNodeType } from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";

export class GenericNode extends BaseSingleFileNode<
  GenericNodeType,
  GenericNodeContext
> {
  getNodeClassBodyStatements(): AstNode[] {
    const statements: AstNode[] = [];
    this.nodeData.attributes.forEach((attribute) => {
      statements.push(
        python.field({
          name: toPythonSafeSnakeCase(attribute.name),
          initializer: new WorkflowValueDescriptor({
            workflowValueDescriptor: attribute.value,
            workflowContext: this.workflowContext,
          }),
        })
      );
    });

    statements.push(
      new NodeTrigger({
        nodeTrigger: this.nodeData.trigger,
        nodeContext: this.nodeContext,
      }),
      new NodePorts({
        nodePorts: this.nodeData.ports,
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
      }),
      new NodeOutput({
        nodeOutputs: this.nodeData.outputs,
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
      })
    );
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
}
