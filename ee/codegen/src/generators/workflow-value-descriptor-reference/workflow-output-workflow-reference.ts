import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeInputNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { Writer } from "src/generators/extensions/writer";
import {
  WorkflowDataNode,
  WorkflowOutputWorkflowReference as WorkflowOutputWorkflowReferenceType,
} from "src/types/vellum";

export declare namespace WorkflowOutputWorkflowReference {
  export interface Args {
    nodeContext?: BaseNodeContext<WorkflowDataNode>;
    workflowContext: WorkflowContext;
    nodeInputWorkflowReferencePointer: WorkflowOutputWorkflowReferenceType;
  }
}

export class WorkflowOutputWorkflowReference extends AstNode {
  protected readonly nodeContext?: BaseNodeContext<WorkflowDataNode>;
  public readonly workflowContext: WorkflowContext;
  public readonly nodeInputWorkflowReferencePointer: WorkflowOutputWorkflowReferenceType;
  private astNode: AstNode | undefined;

  constructor({
    nodeContext,
    workflowContext,
    nodeInputWorkflowReferencePointer,
  }: WorkflowOutputWorkflowReference.Args) {
    super();

    this.nodeContext = nodeContext;
    this.workflowContext = workflowContext;
    this.nodeInputWorkflowReferencePointer = nodeInputWorkflowReferencePointer;

    this.astNode = this.getAstNode();
    if (this.astNode) {
      this.inheritReferences(this.astNode);
    }
  }

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

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
