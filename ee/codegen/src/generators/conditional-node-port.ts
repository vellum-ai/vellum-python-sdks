import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { OperatorType } from "@fern-api/python-ast/OperatorType";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import {
  NodeAttributeGenerationError,
  NodePortGenerationError,
  ValueGenerationError,
} from "./errors";

import * as codegen from "src/codegen";
import { PortContext } from "src/context/port-context";
import { Expression } from "src/generators/expression";
import { NodeInput } from "src/generators/node-inputs";
import {
  ConditionalNodeConditionData,
  ConditionalRuleData,
  ConstantValuePointer,
} from "src/types/vellum";
import { isNilOrEmpty } from "src/utils/typing";

export declare namespace ConditionalNodePort {
  export interface Args {
    portContext: PortContext;
    inputFieldKeysByRuleId: Map<string, string>;
    valueInputKeysByRuleId: Map<string, string>;
    conditionDataWithIndex: [number, ConditionalNodeConditionData];
    nodeInputsByKey: Map<string, NodeInput>;
    nodeLabel: string;
  }
}

export class ConditionalNodePort extends AstNode {
  private portContext: PortContext;
  private conditionalNodeData: ConditionalNodeConditionData;
  private conditionalNodeDataIndex: number;
  private inputFieldKeysByRuleId: Map<string, string>;
  private valueInputKeysByRuleId: Map<string, string>;
  private nodeInputsByKey: Map<string, NodeInput>;
  private astNode: AstNode;
  private nodeLabel: string;

  public constructor(args: ConditionalNodePort.Args) {
    super();

    this.portContext = args.portContext;
    this.inputFieldKeysByRuleId = args.inputFieldKeysByRuleId;
    this.valueInputKeysByRuleId = args.valueInputKeysByRuleId;
    this.conditionalNodeDataIndex = args.conditionDataWithIndex[0];
    this.conditionalNodeData = args.conditionDataWithIndex[1];
    this.nodeInputsByKey = args.nodeInputsByKey;
    this.nodeLabel = args.nodeLabel;
    this.astNode = this.constructPort();
    this.inheritReferences(this.astNode);
  }

  private constructPort(): AstNode {
    return python.invokeMethod({
      methodReference: python.reference({
        name: "Port",
        modulePath:
          this.portContext.workflowContext.sdkModulePathNames.PORTS_MODULE_PATH,
        attribute: [
          this.convertConditionTypeToPortAttribute(
            this.conditionalNodeData.type
          ),
        ],
      }),
      arguments_: (() => {
        const arg = this.generatePortCondition();
        return arg ? [arg] : [];
      })(),
    });
  }

  private generatePortCondition() {
    const conditionData = this.conditionalNodeData.data;
    if (conditionData) {
      return new MethodArgument({
        value: this.buildCondition(conditionData),
      });
    } else {
      return undefined;
    }
  }

  private buildCondition(
    conditionData: ConditionalRuleData | undefined,
    ruleIdx: number = -1
  ): AstNode {
    if (!conditionData) {
      return python.TypeInstantiation.none();
    }

    if (conditionData && conditionData.fieldNodeInputId) {
      return this.buildDescriptor(conditionData, ruleIdx);
    }

    const otherConditions = (conditionData.rules || []).map((rule, idx) => {
      return this.buildCondition(rule, idx);
    });

    const combine =
      conditionData.combinator === "AND"
        ? (lhs: AstNode, rhs: AstNode): AstNode => {
            return python.operator({
              operator: OperatorType.And,
              lhs: lhs,
              rhs: rhs,
            });
          }
        : (lhs: AstNode, rhs: AstNode): AstNode => {
            return python.operator({
              operator: OperatorType.Or,
              lhs: lhs,
              rhs: rhs,
            });
          };

    return otherConditions.reduce((prev, curr) => {
      return combine(prev, curr);
    });
  }

  private convertConditionTypeToPortAttribute(conditionType: string): string {
    switch (conditionType) {
      case "IF":
        return "on_if";
      case "ELIF":
        return "on_elif";
      default:
        return "on_else";
    }
  }

  private buildDescriptor(
    conditionData: ConditionalRuleData,
    ruleIdx: number
  ): AstNode {
    const ruleId = conditionData.id;

    const lhsKey = this.inputFieldKeysByRuleId.get(ruleId);
    let rhsKey;
    if (isNil(lhsKey)) {
      throw new NodeAttributeGenerationError(
        `Could not find input field key given ruleId: ${ruleId} on rule index: ${ruleIdx} on condition index: ${this.conditionalNodeDataIndex} for node: ${this.nodeLabel}`
      );
    }
    if (conditionData.valueNodeInputId) {
      rhsKey = this.valueInputKeysByRuleId.get(ruleId);
    }
    const lhs = this.nodeInputsByKey.get(lhsKey);
    if (isNil(lhs)) {
      throw new NodePortGenerationError(
        `Node ${this.nodeLabel} is missing required left-hand side input field with key: ${lhsKey} for rule: ${ruleIdx} in condition: ${this.conditionalNodeDataIndex}`
      );
    }
    const operator = conditionData.operator
      ? this.convertOperatorToMethod(conditionData.operator, lhs)
      : undefined;
    if (isNil(operator)) {
      throw new NodePortGenerationError(
        `Node ${this.nodeLabel} is missing required operator for rule: ${ruleIdx} in condition: ${this.conditionalNodeDataIndex}`
      );
    }

    let rhs;
    rhs = !isNil(rhsKey) ? this.nodeInputsByKey.get(rhsKey) : undefined;
    // The following is to account for an edge case where we are getting bad data
    // from the UI. Numeric operators are being sent with rhs as STRINGS when they should
    // be NUMBERS
    if (
      rhs &&
      this.isNumericOperator(operator) &&
      this.isConstantStringPointer(rhs)
    ) {
      const nodeValue = rhs.nodeInputData.value
        .rules[0] as ConstantValuePointer;
      const castedValue = Number(nodeValue.data.value);
      if (isNaN(castedValue)) {
        const error = new ValueGenerationError(
          `Failed to cast constant value ${nodeValue.data.value} to NUMBER for attribute ${this.nodeLabel}.${rhsKey}`
        );
        this.portContext.workflowContext.addError(error);
      } else {
        const castedRhs = {
          id: rhs.nodeInputData.id,
          key: rhs.nodeInputData.key,
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE" as const,
                data: {
                  type: "NUMBER",
                  value: castedValue,
                },
              } as ConstantValuePointer,
            ],
            combinator: "OR" as const,
          },
        };
        rhs = codegen.nodeInput({
          nodeContext: this.portContext.nodeContext,
          nodeInputData: castedRhs,
        });
      }
    }

    return new Expression({
      lhs: lhs,
      operator: operator,
      rhs: rhs,
      workflowContext: this.portContext.workflowContext,
    });
  }

  private convertOperatorToMethod(operator: string, lhs: NodeInput): string {
    // Legacy conditional nodes in legacy workflows assumed `is_nil` functionality
    // for the `null` operator. This workaround is to support that cutover.
    const isNodeOutput =
      lhs.nodeInputData.value.rules[0]?.type === "NODE_OUTPUT";
    const operatorMappings: { [key: string]: string } = {
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
      null: isNodeOutput ? "is_nil" : "is_null",
      notNull: isNodeOutput ? "is_not_nil" : "is_not_null",
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
  }

  private isNumericOperator(operator: string): boolean {
    return new Set([
      "less_than",
      "greater_than",
      "less_than_or_equal_to",
      "greater_than_or_equal_to",
    ]).has(operator);
  }

  private isConstantStringPointer(input: NodeInput): boolean {
    return (
      !isNilOrEmpty(input.nodeInputData.value.rules) &&
      input.nodeInputData.value.rules[0]?.type === "CONSTANT_VALUE" &&
      input.nodeInputData.value.rules[0]?.data.type === "STRING"
    );
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
