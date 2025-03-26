import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { Expression } from "src/generators/expression";
import { WorkflowValueDescriptorReference } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference";
import {
  IterableConfig,
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";
import {
  convertOperatorType,
  isReference,
} from "src/utils/workflow-value-descriptor";

export namespace WorkflowValueDescriptor {
  export interface Args {
    nodeContext?: BaseNodeContext<WorkflowDataNode>;
    workflowValueDescriptor?: WorkflowValueDescriptorType;
    workflowContext: WorkflowContext;
    iterableConfig?: IterableConfig;
  }
}

export class WorkflowValueDescriptor extends AstNode {
  private nodeContext?: BaseNodeContext<WorkflowDataNode>;
  private workflowContext: WorkflowContext;
  private iterableConfig?: IterableConfig;
  private astNode: AstNode;

  public constructor(args: WorkflowValueDescriptor.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    this.iterableConfig = args.iterableConfig;
    this.astNode = this.generateWorkflowValueDescriptor(
      args.workflowValueDescriptor
    );
    this.inheritReferences(this.astNode);
  }

  private generateWorkflowValueDescriptor(
    workflowValueDescriptor: WorkflowValueDescriptorType | undefined
  ): AstNode {
    if (isNil(workflowValueDescriptor)) {
      return python.TypeInstantiation.none();
    }
    return this.buildExpression(workflowValueDescriptor);
  }

  private buildExpression(
    workflowValueDescriptor: WorkflowValueDescriptorType | undefined
  ): AstNode {
    if (!workflowValueDescriptor) {
      return python.TypeInstantiation.none();
    }

    // Base case
    if (isReference(workflowValueDescriptor)) {
      const reference = new WorkflowValueDescriptorReference({
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
        workflowValueReferencePointer: workflowValueDescriptor,
        iterableConfig: this.iterableConfig,
      });

      if (!reference.astNode) {
        return python.TypeInstantiation.none();
      }

      return reference;
    }

    switch (workflowValueDescriptor.type) {
      case "UNARY_EXPRESSION": {
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const operator = convertOperatorType(workflowValueDescriptor);
        return new Expression({
          lhs,
          operator: operator,
        });
      }
      case "BINARY_EXPRESSION": {
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const rhs = this.buildExpression(workflowValueDescriptor.rhs);
        const operator = convertOperatorType(workflowValueDescriptor);
        return new Expression({
          lhs,
          operator: operator,
          rhs,
        });
      }
      case "TERNARY_EXPRESSION": {
        const base = this.buildExpression(workflowValueDescriptor.base);
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const rhs = this.buildExpression(workflowValueDescriptor.rhs);
        const operator = convertOperatorType(workflowValueDescriptor);
        return new Expression({
          lhs: lhs,
          operator: operator,
          rhs: rhs,
          base: base,
        });
      }
      default:
        assertUnreachable(workflowValueDescriptor);
    }
  }

  write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
