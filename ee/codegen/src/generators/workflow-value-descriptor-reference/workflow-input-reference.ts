import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { NodeInputNotFoundError } from "src/generators/errors";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { WorkflowInputWorkflowReference as WorkflowInputWorkflowReferenceType } from "src/types/vellum";

export class WorkflowInputReference extends BaseNodeInputWorkflowReference<WorkflowInputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const workflowInputReference = this.nodeInputWorkflowReferencePointer;

    const inputVariableContext =
      this.workflowContext.findInputVariableContextById(
        workflowInputReference.inputVariableId
      );

    if (!inputVariableContext) {
      const pathInfo = this.nodeContext
        ? `node: ${this.nodeContext.getNodeLabel()}`
        : "workflow";
      const attributeInfo = this.attributeConfig?.lhs?.name
        ? `, attribute: ${this.attributeConfig.lhs.name}`
        : "";

      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find input variable context with id ${workflowInputReference.inputVariableId} (${pathInfo}${attributeInfo})`,
          "WARNING"
        )
      );
      return python.TypeInstantiation.none();
    }
    return python.reference({
      name: inputVariableContext.definition.name,
      modulePath: inputVariableContext.definition.module,
      attribute: [inputVariableContext.name],
    });
  }
}
