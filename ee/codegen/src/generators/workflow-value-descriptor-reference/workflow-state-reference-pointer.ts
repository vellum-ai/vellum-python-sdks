import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReferencePointer";
import { WorkflowStateVariableWorkflowReference as WorkflowStateVariableWorkflowReferenceType } from "src/types/vellum";

export class WorkflowStateReferencePointer extends BaseNodeInputWorkflowReferencePointer<WorkflowStateVariableWorkflowReferenceType> {
  // TODO: Implement this
  getAstNode(): AstNode | undefined {
    return undefined;
  }
}
