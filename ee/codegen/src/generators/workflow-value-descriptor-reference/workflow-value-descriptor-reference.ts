import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import { ValueGenerationError } from "src/generators/errors";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { ConstantValueReference } from "src/generators/workflow-value-descriptor-reference/constant-value-reference";
import { ExecutionCounterWorkflowReference } from "src/generators/workflow-value-descriptor-reference/execution-counter-workflow-reference";
import { NodeOutputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/node-output-workflow-reference";
import { VellumSecretWorkflowReference } from "src/generators/workflow-value-descriptor-reference/vellum-secret-workflow-reference";
import { WorkflowInputReference } from "src/generators/workflow-value-descriptor-reference/workflow-input-reference";
import {
  IterableConfig,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export declare namespace WorkflowValueDescriptorReference {
  export interface Args {
    workflowContext: WorkflowContext;
    workflowValueReferencePointer: WorkflowValueDescriptorReferenceType;
    iterableConfig?: IterableConfig;
  }
}

export class WorkflowValueDescriptorReference extends AstNode {
  private workflowContext: WorkflowContext;
  public readonly workflowValueReferencePointer: WorkflowValueDescriptorReferenceType["type"];
  private iterableConfig?: IterableConfig;
  public astNode:
    | BaseNodeInputWorkflowReference<WorkflowValueDescriptorReferenceType>
    | undefined;

  constructor(args: WorkflowValueDescriptorReference.Args) {
    super();

    this.workflowContext = args.workflowContext;
    this.workflowValueReferencePointer =
      args.workflowValueReferencePointer.type;
    this.iterableConfig = args.iterableConfig;

    this.astNode = this.getAstNode(args.workflowValueReferencePointer);

    if (this.astNode) {
      this.inheritReferences(this.astNode);
    }
  }

  private getAstNode(
    workflowValueReferencePointer: WorkflowValueDescriptorReferenceType
  ):
    | BaseNodeInputWorkflowReference<WorkflowValueDescriptorReferenceType>
    | undefined {
    const referenceType = workflowValueReferencePointer.type;

    switch (referenceType) {
      case "NODE_OUTPUT": {
        const reference = new NodeOutputWorkflowReference({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
        if (reference.getAstNode()) {
          return reference;
        } else {
          return undefined;
        }
      }
      case "WORKFLOW_INPUT":
        return new WorkflowInputReference({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "WORKFLOW_STATE":
        this.workflowContext.addError(
          new ValueGenerationError(
            "WORKFLOW_STATE reference pointers is not implemented"
          )
        );
        return undefined;
      case "CONSTANT_VALUE":
        return new ConstantValueReference({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
          iterableConfig: this.iterableConfig,
        });
      case "VELLUM_SECRET":
        return new VellumSecretWorkflowReference({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "EXECUTION_COUNTER":
        return new ExecutionCounterWorkflowReference({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      default: {
        assertUnreachable(referenceType);
      }
    }
  }

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
