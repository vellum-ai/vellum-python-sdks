import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import {
  NodeAttributeGenerationError,
  NodePortGenerationError,
} from "src/generators/errors";
import { Expression } from "src/generators/expression";
import { WorkflowValueDescriptorReference } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference";
import {
  IterableConfig,
  OperatorMapping,
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export namespace WorkflowValueDescriptor {
  export interface Args {
    nodeContext?: BaseNodeContext<WorkflowDataNode>;
    workflowValueDescriptor: WorkflowValueDescriptorType;
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
    workflowValueDescriptor: WorkflowValueDescriptorType
  ): AstNode {
    if (isNil(workflowValueDescriptor)) {
      return python.TypeInstantiation.none();
    }
    return this.buildExpression(workflowValueDescriptor);
  }

  private buildExpression(
    workflowValueDescriptor: WorkflowValueDescriptorType
  ): AstNode {
    // Base case
    if (this.isReference(workflowValueDescriptor)) {
      return new WorkflowValueDescriptorReference({
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
        nodeContext: this.nodeContext,
        workflowValueReferencePointer: workflowValueDescriptor,
        iterableConfig: this.iterableConfig,
      });
    }

    switch (workflowValueDescriptor.type) {
      case "UNARY_EXPRESSION": {
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const operator = this.convertOperatorType(workflowValueDescriptor);
        return new Expression({
          lhs,
          operator: operator,
        });
      }
      case "BINARY_EXPRESSION": {
        const lhs = this.buildExpression(workflowValueDescriptor.lhs);
        const rhs = this.buildExpression(workflowValueDescriptor.rhs);
        const operator = this.convertOperatorType(workflowValueDescriptor);
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
        const operator = this.convertOperatorType(workflowValueDescriptor);
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

  private convertOperatorType(
    workflowValueDescriptor: WorkflowValueDescriptorType
  ): OperatorMapping {
    if (this.isExpression(workflowValueDescriptor)) {
      const operator = workflowValueDescriptor.operator;
      const operatorMappings: Record<string, OperatorMapping> = {
        "=": "equals",
        "!=": "does_not_equal",
        "<": "less_than",
        ">": "greater_than",
        "<=": "less_than_or_equal_to",
        ">=": "greater_than_or_equal_to",
        contains: "contains",
        beginsWith: "begins_with",
        endsWith: "ends_with",
        doesNotContain: "does_not_contain",
        doesNotBeginWith: "does_not_begin_with",
        doesNotEndWith: "does_not_end_with",
        null: "is_null",
        notNull: "is_not_null",
        in: "in",
        notIn: "not_in",
        between: "between",
        notBetween: "not_between",
      };
      const value = operatorMappings[operator];
      if (!value) {
        throw new NodePortGenerationError(
          `This operator: ${operator} is not supported`
        );
      }
      return value;
    } else {
      throw new NodeAttributeGenerationError(
        `Operators should exist on expression and not be null`
      );
    }
  }

  private isExpression(workflowValueDescriptor: WorkflowValueDescriptorType) {
    return (
      workflowValueDescriptor.type === "UNARY_EXPRESSION" ||
      workflowValueDescriptor.type === "BINARY_EXPRESSION" ||
      workflowValueDescriptor.type === "TERNARY_EXPRESSION"
    );
  }

  private isReference(workflowValueDescriptor: WorkflowValueDescriptorType) {
    return (
      workflowValueDescriptor.type === "NODE_OUTPUT" ||
      workflowValueDescriptor.type === "WORKFLOW_INPUT" ||
      workflowValueDescriptor.type === "WORKFLOW_STATE" ||
      workflowValueDescriptor.type === "CONSTANT_VALUE" ||
      workflowValueDescriptor.type === "VELLUM_SECRET" ||
      workflowValueDescriptor.type === "EXECUTION_COUNTER"
    );
  }

  write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
