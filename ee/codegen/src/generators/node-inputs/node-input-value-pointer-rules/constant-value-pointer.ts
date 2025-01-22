import { BaseNodeInputValuePointerRule } from "./base";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { VellumValue } from "src/generators";
import { IterableConfig } from "src/generators/vellum-variable-value";
import { ConstantValuePointer } from "src/types/vellum";

export declare namespace ConstantValuePointerRule {
  interface Args {
    workflowContext: WorkflowContext;
    nodeInputValuePointerRule: ConstantValuePointer;
    iterableConfig?: IterableConfig;
  }
}

export class ConstantValuePointerRule extends BaseNodeInputValuePointerRule<ConstantValuePointer> {
  constructor(args: ConstantValuePointerRule.Args) {
    super(args);
  }

  getAstNode(): VellumValue {
    const constantValuePointerRuleData = this.nodeInputValuePointerRule.data;

    return codegen.vellumValue({
      vellumValue: constantValuePointerRuleData,
      iterableConfig: this.iterableConfig,
    });
  }
}
