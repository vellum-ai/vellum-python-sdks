import { BaseNodeInputValuePointerRule } from "./base";

import { Reference } from "src/generators/extensions/reference";
import { ExecutionCounterPointer } from "src/types/vellum";

export class ExecutionCounterPointerRule extends BaseNodeInputValuePointerRule<ExecutionCounterPointer> {
  getReferencedNodeContext() {
    const executionCounterData = this.nodeInputValuePointerRule.data;

    return this.workflowContext.findNodeContext(executionCounterData.nodeId);
  }

  getAstNode(): Reference | undefined {
    const nodeContext = this.getReferencedNodeContext();

    if (!nodeContext) {
      return undefined;
    }

    return new Reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: ["Execution", "count"],
    });
  }
}
