import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReferencePointer";
import { ExecutionCounterWorkflowReference as ExecutionCounterWorkflowReferenceType } from "src/types/vellum";

export class ExecutionCounterWorkflowReferencePointer extends BaseNodeInputWorkflowReferencePointer<ExecutionCounterWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const executionCounterNodeId =
      this.nodeInputWorkflowReferencePointer.nodeId;

    const nodeContext = this.workflowContext.getNodeContext(
      executionCounterNodeId
    );

    return python.reference({
      name: nodeContext.nodeClassName,
      modulePath: nodeContext.nodeModulePath,
      attribute: ["Execution", "count"],
    });
  }
}
