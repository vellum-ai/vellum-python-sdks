import { BaseNodeInputValuePointerRule } from "./base";

import * as codegen from "src/codegen";
import { BaseNodeContext } from "src/context/node-context/base";
import { AstNode } from "src/generators/extensions/ast-node";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  ConstantValuePointer,
  IterableConfig,
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";

export declare namespace ConstantValuePointerRule {
  interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    nodeInputValuePointerRule: ConstantValuePointer;
    iterableConfig?: IterableConfig;
  }
}

const EXPRESSION_TYPES = new Set([
  "UNARY_EXPRESSION",
  "BINARY_EXPRESSION",
  "TERNARY_EXPRESSION",
]);

const REFERENCE_TYPES = new Set([
  "NODE_OUTPUT",
  "WORKFLOW_INPUT",
  "WORKFLOW_OUTPUT",
  "WORKFLOW_STATE",
  "CONSTANT_VALUE",
  "VELLUM_SECRET",
  "ENVIRONMENT_VARIABLE",
  "EXECUTION_COUNTER",
  "DICTIONARY_REFERENCE",
  "ARRAY_REFERENCE",
  "TRIGGER_ATTRIBUTE",
]);

function isWorkflowValueDescriptor(
  value: unknown
): value is WorkflowValueDescriptorType {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const obj = value as Record<string, unknown>;
  if (typeof obj.type !== "string") {
    return false;
  }
  return EXPRESSION_TYPES.has(obj.type) || REFERENCE_TYPES.has(obj.type);
}

export class ConstantValuePointerRule extends BaseNodeInputValuePointerRule<ConstantValuePointer> {
  constructor(args: ConstantValuePointerRule.Args) {
    super(args);
  }

  getAstNode(): AstNode {
    const constantValuePointerRuleData = this.nodeInputValuePointerRule.data;

    if (
      constantValuePointerRuleData.type === "JSON" &&
      isWorkflowValueDescriptor(constantValuePointerRuleData.value)
    ) {
      return new WorkflowValueDescriptor({
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
        workflowValueDescriptor: constantValuePointerRuleData.value,
        iterableConfig: this.iterableConfig,
      });
    }

    return codegen.vellumValue({
      vellumValue: constantValuePointerRuleData,
      iterableConfig: this.iterableConfig,
    });
  }
}
