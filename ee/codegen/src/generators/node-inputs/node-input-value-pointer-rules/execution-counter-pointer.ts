import { python } from "@fern-api/python-ast";

import { BaseNodeInputValuePointerRule } from "./base";

import { BaseNodeContext } from "src/context/node-context/base";
import { ExecutionCounterPointer, WorkflowDataNode } from "src/types/vellum";

export class ExecutionCounterPointerRule extends BaseNodeInputValuePointerRule<ExecutionCounterPointer> {
  getReferencedNodeContext(): BaseNodeContext<WorkflowDataNode> {
    const executionCounterData = this.nodeInputValuePointerRule.data;

    return this.workflowContext.getNodeContext(executionCounterData.nodeId);
  }

  getAstNode(): python.Reference {
    const nodeContext = this.getReferencedNodeContext();

    return python.reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: ["Execution", "count"],
    });
  }
}
