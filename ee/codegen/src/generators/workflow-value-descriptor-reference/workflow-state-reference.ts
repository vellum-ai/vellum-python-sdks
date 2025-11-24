import { python } from "@fern-api/python-ast";

import { BaseNodeInputWorkflowReference } from "./BaseNodeInputWorkflowReference";

import { NodeInputNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { WorkflowStateVariableWorkflowReference as WorkflowStateVariableWorkflowReferenceType } from "src/types/vellum";

export class WorkflowStateReference extends BaseNodeInputWorkflowReference<WorkflowStateVariableWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const workflowStateReference = this.nodeInputWorkflowReferencePointer;

    const stateVariableContext =
      this.workflowContext.findStateVariableContextById(
        workflowStateReference.stateVariableId
      );

    if (!stateVariableContext) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find state variable context with id ${workflowStateReference.stateVariableId}`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }
    return python.reference({
      name: stateVariableContext.definition.name,
      modulePath: stateVariableContext.definition.module,
      attribute: [stateVariableContext.name],
    });
  }
}
