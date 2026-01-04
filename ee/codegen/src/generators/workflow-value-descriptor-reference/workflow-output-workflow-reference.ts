import { NodeInputNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { WorkflowOutputWorkflowReference as WorkflowOutputWorkflowReferenceType } from "src/types/vellum";

export class WorkflowOutputWorkflowReference extends BaseNodeInputWorkflowReference<WorkflowOutputWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const workflowOutputReference = this.nodeInputWorkflowReferencePointer;

    const outputVariableContext =
      this.workflowContext.findOutputVariableContextById(
        workflowOutputReference.outputVariableId
      );

    if (!outputVariableContext) {
      const pathInfo = this.nodeContext
        ? `node: ${this.nodeContext.getNodeLabel()}`
        : "workflow";

      this.workflowContext.addError(
        new NodeInputNotFoundError(
          `Could not find output variable context with id ${workflowOutputReference.outputVariableId} (${pathInfo})`,
          "WARNING"
        )
      );
      return new NoneInstantiation();
    }

    return new Reference({
      name: this.workflowContext.workflowClassName,
      modulePath: this.workflowContext.modulePath,
      attribute: ["Outputs", outputVariableContext.name],
    });
  }
}
