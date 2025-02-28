import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { ExecutionCounterWorkflowReference as ExecutionCounterWorkflowReferenceType } from "src/types/vellum";

export class ExecutionCounterWorkflowReference extends BaseNodeInputWorkflowReference<ExecutionCounterWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const executionCounterNodeId =
      this.nodeInputWorkflowReferencePointer.nodeId;

    const nodeContext = this.workflowContext.findNodeContext(
      executionCounterNodeId
    );

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
