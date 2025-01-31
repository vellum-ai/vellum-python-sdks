import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { NodeInputNotFoundError } from "src/generators/errors";
import { BaseNodeInputWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReferencePointer";
import { WorkflowInputWorkflowReference as WorkflowInputWorkflowReferenceType } from "src/types/vellum";

export class WorkflowInputReferencePointer extends BaseNodeInputWorkflowReferencePointer<WorkflowInputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const workflowInputReference = this.nodeInputWorkflowReferencePointer;

    const inputVariableContext =
      this.workflowContext.findInputVariableContextById(
        workflowInputReference.inputVariableId
      );

    if (!inputVariableContext) {
      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find input variable context with id ${workflowInputReference.inputVariableId}`
        )
      );
      return python.TypeInstantiation.none();
    }
    return python.reference({
      name: "Inputs",
      modulePath: inputVariableContext.modulePath,
      attribute: [inputVariableContext.name],
    });
  }
}
