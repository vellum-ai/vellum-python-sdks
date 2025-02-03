import { BaseNodeInputValuePointerRule } from "./base";

import * as codegen from "src/codegen";
import { BaseNodeContext } from "src/context/node-context/base";
import { VellumValue } from "src/generators";
import {
  ConstantValuePointer,
  IterableConfig,
  WorkflowDataNode,
} from "src/types/vellum";

export declare namespace ConstantValuePointerRule {
  interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
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
