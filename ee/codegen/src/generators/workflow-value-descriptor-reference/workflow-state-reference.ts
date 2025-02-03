import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { WorkflowStateVariableWorkflowReference as WorkflowStateVariableWorkflowReferenceType } from "src/types/vellum";

export class WorkflowStateReference extends BaseNodeInputWorkflowReference<WorkflowStateVariableWorkflowReferenceType> {
  // TODO: Implement this
  getAstNode(): AstNode | undefined {
    return undefined;
  }
}
