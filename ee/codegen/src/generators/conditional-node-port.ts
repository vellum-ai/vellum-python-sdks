import { python } from "@fern-api/python-ast";
import { MethodArgument } from "@fern-api/python-ast/MethodArgument";
import { OperatorType } from "@fern-api/python-ast/OperatorType";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { PortContext } from "src/context/port-context";
import { NodeInputValuePointer } from "src/generators/node-inputs";
import {
  ConditionalNodeConditionData,
  ConditionalRuleData,
  ExecutionCounterData,
  InputVariableData,
  NodeInput as NodeInputType,
  NodeInputValuePointer as NodeInputValuePointerType,
  NodeOutputData,
  WorkspaceSecretData,
} from "src/types/vellum";
import { toSnakeCase } from "src/utils/casing";
import { assertUnreachable } from "src/utils/typing";

export declare namespace ConditionalNodePort {
  export interface Args {
    portContext: PortContext;
    inputFieldsByRuleId: Map<string, NodeInputType>;
    valueInputsByRuleIds: Map<string, NodeInputValuePointerType>;
    conditionData: ConditionalNodeConditionData;
  }
}

export class ConditionalNodePort extends AstNode {
  private portContext: PortContext;
  private conditionalNodeData: ConditionalNodeConditionData;
  private inputFieldsByRuleId: Map<string, NodeInputType>;
  private valueInputsByRuleIds: Map<string, NodeInputValuePointerType>;
  private astNode: AstNode;

  public constructor(args: ConditionalNodePort.Args) {
    super();

    this.portContext = args.portContext;
    this.inputFieldsByRuleId = args.inputFieldsByRuleId;
    this.valueInputsByRuleIds = args.valueInputsByRuleIds;
    this.conditionalNodeData = args.conditionData;
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
    conditionData: ConditionalRuleData | undefined
  ): AstNode {
    if (!conditionData) {
      return python.TypeInstantiation.none();
    }

    if (
      conditionData &&
      conditionData.fieldNodeInputId &&
      conditionData.valueNodeInputId
    ) {
      return this.buildDescriptor(conditionData);
    }

    const otherConditions = (conditionData.rules || []).map((rule) => {
      return this.buildCondition(rule);
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

    const combinedConditions = otherConditions.reduce((prev, curr) => {
      return combine(prev, curr);
    });
    return combinedConditions;
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

  private buildDescriptor(conditionData: ConditionalRuleData): AstNode {
    const ruleId = conditionData.id;
    const fieldInput = this.inputFieldsByRuleId.get(ruleId);
    if (!fieldInput) {
      throw new Error(`No input found given ${ruleId}`);
    }

    const rule = fieldInput.value.rules[0];
    if (!rule) {
      throw new Error(`No node input pointer for rule ${ruleId}`);
    }
    let fieldInputRef;
    switch (rule.type) {
      case "CONSTANT_VALUE": {
        throw new Error(
          "Descriptors with a constant value on the left hand side is not supported"
        );
      }
      case "NODE_OUTPUT": {
        const data = rule.data as NodeOutputData;
        const nodeContext = this.portContext.workflowContext.getNodeContext(
          data.nodeId
        );
        fieldInputRef = python.reference({
          name: nodeContext.getNodeOutputNameById(data.outputId),
          modulePath: nodeContext.nodeModulePath,
          attribute: (() => {
            return conditionData.operator
              ? [this.convertOperatorToMethod(conditionData.operator)]
              : [];
          })(),
        });
        break;
      }
      case "INPUT_VARIABLE": {
        const data = rule.data as InputVariableData;
        const inputContext =
          this.portContext.workflowContext.getInputVariableContextById(
            data.inputVariableId
          );
        fieldInputRef = python.reference({
          name: "Inputs",
          modulePath: inputContext.modulePath,
          attribute: (() => {
            return conditionData.operator
              ? [
                  toSnakeCase(inputContext.getInputVariableName()),
                  this.convertOperatorToMethod(conditionData.operator),
                ]
              : [];
          })(),
        });
        break;
      }
      case "WORKSPACE_SECRET": {
        const data = rule.data as WorkspaceSecretData;
        if (data.workspaceSecretId) {
          fieldInputRef = python.reference({
            name: "VellumSecretReference",
            modulePath: [
              ...this.portContext.workflowContext.sdkModulePathNames
                .WORKFLOWS_MODULE_PATH,
              "references",
            ],
            attribute: (() => {
              return conditionData.operator
                ? [
                    data.workspaceSecretId,
                    this.convertOperatorToMethod(conditionData.operator),
                  ]
                : [];
            })(),
          });
        }
        break;
      }
      case "EXECUTION_COUNTER": {
        const data = rule.data as ExecutionCounterData;
        const nodeContext = this.portContext.nodeContext;
        fieldInputRef = python.reference({
          name: nodeContext.getNodeOutputNameById(data.nodeId),
          modulePath: nodeContext.nodeModulePath,
          attribute: (() => {
            return conditionData.operator
              ? [
                  "Execution",
                  "count",
                  this.convertOperatorToMethod(conditionData.operator),
                ]
              : [];
          })(),
        });
        break;
      }
      default: {
        assertUnreachable(rule);
      }
    }

    if (!fieldInputRef) {
      throw new Error("No reference made for field input");
    }

    return python.invokeMethod({
      methodReference: fieldInputRef,
      arguments_: (() => {
        const value = this.valueInputsByRuleIds.get(ruleId);
        return value
          ? [
              new MethodArgument({
                value: new NodeInputValuePointer({
                  workflowContext: this.portContext.workflowContext,
                  nodeInputValuePointerData: value,
                }),
              }),
            ]
          : [];
      })(),
    });
  }

  private convertOperatorToMethod(operator: string): string {
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
      null: "is_null",
      notNull: "is_not_null",
      in: "in",
      notIn: "not_in",
      between: "between",
      notBetween: "not_between",
    };
    const value = operatorMappings[operator];
    if (!value) {
      throw new Error(`This operator: ${operator} is not supported`);
    }
    return value;
  }

  public write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
