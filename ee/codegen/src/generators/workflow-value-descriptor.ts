import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { ValueGenerationError } from "src/generators/errors";
import { Expression } from "src/generators/expression";
import { WorkflowValueDescriptorReference } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference";
import {
  AttributeConfig,
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
    workflowValueDescriptor?: WorkflowValueDescriptorType | null;
    workflowContext: WorkflowContext;
    iterableConfig?: IterableConfig;
    attributeConfig?: AttributeConfig;
  }
}

export class WorkflowValueDescriptor extends AstNode {
  private nodeContext?: BaseNodeContext<WorkflowDataNode>;
  private workflowContext: WorkflowContext;
  private iterableConfig?: IterableConfig;
  private attributeConfig?: AttributeConfig;
  private astNode: AstNode;

  public constructor(args: WorkflowValueDescriptor.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    this.iterableConfig = args.iterableConfig;
    this.attributeConfig = args.attributeConfig;
    this.astNode = this.generateWorkflowValueDescriptor(
      args.workflowValueDescriptor
    );
    this.inheritReferences(this.astNode);
  }

  private generateWorkflowValueDescriptor(
    workflowValueDescriptor: WorkflowValueDescriptorType | null | undefined
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
        attributeConfig: this.attributeConfig,
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
          workflowContext: this.workflowContext,
        });
      }
      case "BINARY_EXPRESSION": {
        if (
          workflowValueDescriptor.operator === "coalesce" &&
          workflowValueDescriptor.lhs === null
        ) {
          this.workflowContext.addError(
            new ValueGenerationError(
              "Skipping null LHS in coalesce expression, using only RHS value",
              "WARNING"
            )
          );
          return this.buildExpression(workflowValueDescriptor.rhs);
        }

        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const rhs = this.buildExpression(workflowValueDescriptor.rhs);
        const operator = convertOperatorType(workflowValueDescriptor);
        return new Expression({
          lhs,
          operator: operator,
          rhs,
          workflowContext: this.workflowContext,
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
          workflowContext: this.workflowContext,
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
