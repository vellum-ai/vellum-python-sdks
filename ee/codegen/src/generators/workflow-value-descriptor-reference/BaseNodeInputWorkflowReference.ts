import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import {
  IterableConfig,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
} from "src/types/vellum";

export declare namespace BaseNodeInputWorkflowReference {
  export interface Args<T extends WorkflowValueDescriptorReferenceType> {
    workflowContext: WorkflowContext;
    nodeInputWorkflowReferencePointer: T;
    iterableConfig?: IterableConfig;
  }
}

export abstract class BaseNodeInputWorkflowReference<
  T extends WorkflowValueDescriptorReferenceType
> extends AstNode {
  public readonly workflowContext: WorkflowContext;
  public readonly nodeInputWorkflowReferencePointer: T;
  public readonly iterableConfig?: IterableConfig;
  private astNode: AstNode | undefined;

  constructor({
    workflowContext,
    nodeInputWorkflowReferencePointer,
    iterableConfig,
  }: BaseNodeInputWorkflowReference.Args<T>) {
    super();

    this.workflowContext = workflowContext;
    this.iterableConfig = iterableConfig;
    this.nodeInputWorkflowReferencePointer = nodeInputWorkflowReferencePointer;

    this.astNode = this.getAstNode();
    if (this.astNode) {
      this.inheritReferences(this.astNode);
    }
  }

  abstract getAstNode(): AstNode | undefined;

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
