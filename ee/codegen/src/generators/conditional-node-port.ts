import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";
import { VellumVariableType } from "vellum-ai/api";

import { NodePortGenerationError, ValueGenerationError } from "./errors";

import * as codegen from "src/codegen";
import { PortContext } from "src/context/port-context";
import { Expression } from "src/generators/expression";
import { NodeInput } from "src/generators/node-inputs";
import {
  AmpersandExpression,
  ParenthesizedExpression,
  PipeExpression,
} from "src/generators/nodes/conditional-node-operator";
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

const NUMERIC_OPERATORS = new Set([
  "less_than",
  "greater_than",
  "less_than_or_equal_to",
  "greater_than_or_equal_to",
]);
const EQUALITY_OPERATORS = new Set(["equals", "does_not_equal"]);

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
            // If rhs is a PipeExpression (OR), wrap it in parentheses for proper precedence
            if (rhs instanceof PipeExpression) {
              rhs = new ParenthesizedExpression({ expression: rhs });
            }
            // If lhs is a PipeExpression (OR), wrap it in parentheses for proper precedence
            if (lhs instanceof PipeExpression) {
              lhs = new ParenthesizedExpression({ expression: lhs });
            }
            return new AmpersandExpression({
              lhs,
              rhs,
            });
          }
        : (lhs: AstNode, rhs: AstNode): AstNode => {
            // If rhs is an AmpersandExpression (AND), wrap it in parentheses for proper precedence
            if (rhs instanceof AmpersandExpression) {
              rhs = new ParenthesizedExpression({ expression: rhs });
            }
            // If lhs is an AmpersandExpression (AND), wrap it in parentheses for proper precedence
            if (lhs instanceof AmpersandExpression) {
              lhs = new ParenthesizedExpression({ expression: lhs });
            }
            return new PipeExpression({ lhs, rhs });
          };

    return otherConditions.length > 0
      ? otherConditions.reduce((prev, curr) => combine(prev, curr))
      : python.TypeInstantiation.none();
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
    if (isNil(lhsKey)) {
      this.portContext.workflowContext.addError(
        new NodePortGenerationError(
          `Node ${this.nodeLabel} is missing required left-hand side input field for rule: ${ruleIdx} in condition: ${this.conditionalNodeDataIndex}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }
    const lhs = this.nodeInputsByKey.get(lhsKey);
    if (isNil(lhs)) {
      this.portContext.workflowContext.addError(
        new NodePortGenerationError(
          `Node ${this.nodeLabel} is missing required left-hand side input field for rule: ${ruleIdx} in condition: ${this.conditionalNodeDataIndex}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }

    const operator = conditionData.operator
      ? this.convertOperatorToMethod(conditionData.operator, lhs)
      : undefined;
    if (isNil(operator)) {
      throw new NodePortGenerationError(
        `Node ${this.nodeLabel} is missing required operator for rule: ${ruleIdx} in condition: ${this.conditionalNodeDataIndex}`
      );
    }

    let rhsKey;
    if (conditionData.valueNodeInputId) {
      rhsKey = this.valueInputKeysByRuleId.get(ruleId);
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
      const castedRhs = this.castStringConstantToNumber(rhs);
      if (castedRhs) {
        rhs = castedRhs;
      }
    }

    // The following is to account for another case where old workflows auto casted strings to numbers
    // when it detected numeric equality operators. This is a workaround to support that cutover.
    if (
      this.isEqualityOperator(operator) &&
      this.inferNodeInputType(lhs) === "NUMBER"
    ) {
      const castedRhs = this.castStringConstantToNumber(rhs);
      if (castedRhs) {
        rhs = castedRhs;
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
      isError: "is_error",
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
    return NUMERIC_OPERATORS.has(operator);
  }

  private isEqualityOperator(operator: string): boolean {
    return EQUALITY_OPERATORS.has(operator);
  }

  private isConstantStringPointer(input: NodeInput): boolean {
    return (
      !isNilOrEmpty(input.nodeInputData.value.rules) &&
      input.nodeInputData.value.rules[0]?.type === "CONSTANT_VALUE" &&
      input.nodeInputData.value.rules[0]?.data.type === "STRING"
    );
  }

  private inferNodeInputType(input: NodeInput): VellumVariableType {
    const rule = input.nodeInputData.value.rules[0];
    if (!rule) {
      return "JSON";
    }

    if (rule.type === "CONSTANT_VALUE") {
      return rule.data.type;
    }

    if (rule.type === "NODE_OUTPUT") {
      const nodeContext = this.portContext.workflowContext.findNodeContext(
        rule.data.nodeId
      );
      if (nodeContext) {
        const outputType = nodeContext.getNodeOutputTypeById(
          rule.data.outputId
        );
        if (outputType) {
          return outputType;
        }
      }
    }

    if (rule.type === "EXECUTION_COUNTER") {
      return "NUMBER";
    }

    if (rule.type === "INPUT_VARIABLE") {
      const inputVariableContext =
        this.portContext.workflowContext.findInputVariableContextById(
          rule.data.inputVariableId
        );
      if (inputVariableContext) {
        return inputVariableContext.getInputVariableData().type;
      }
    }

    if (rule.type === "WORKSPACE_SECRET") {
      return "STRING";
    }

    return "JSON";
  }

  private castStringConstantToNumber(
    nodeInput: NodeInput | undefined
  ): NodeInput | undefined {
    if (isNil(nodeInput)) {
      return undefined;
    }

    const nodeValue = nodeInput.nodeInputData.value
      .rules[0] as ConstantValuePointer;
    const castedValue = Number(nodeValue.data.value);
    if (isNaN(castedValue)) {
      const error = new ValueGenerationError(
        `Failed to cast constant value ${nodeValue.data.value} to NUMBER for attribute ${this.nodeLabel}.${nodeInput.nodeInputData.key}`
      );
      this.portContext.workflowContext.addError(error);
      return;
    } else {
      const castedRhs = {
        id: nodeInput.nodeInputData.id,
        key: nodeInput.nodeInputData.key,
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
      return codegen.nodeInput({
        nodeContext: this.portContext.nodeContext,
        nodeInputData: castedRhs,
      });
    }
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
