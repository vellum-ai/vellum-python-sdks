import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { ExecutionCounterPointer } from "src/types/vellum";

export class ExecutionCounterPointerRule extends BaseNodeInputValuePointerRule<ExecutionCounterPointer> {
  getReferencedNodeContext() {
    const executionCounterData = this.nodeInputValuePointerRule.data;

    return this.workflowContext.findNodeContext(executionCounterData.nodeId);
  }

  getAstNode(): python.Reference | undefined {
    const nodeContext = this.getReferencedNodeContext();

    if (!nodeContext) {
      return undefined;
    }

    return python.reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: ["Execution", "count"],
    });
  }
}
