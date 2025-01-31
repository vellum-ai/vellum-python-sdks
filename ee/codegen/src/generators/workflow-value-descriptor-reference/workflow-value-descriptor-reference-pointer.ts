import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import { ValueGenerationError } from "src/generators/errors";
import { BaseNodeInputWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReferencePointer";
import { ConstantValueReferencePointer } from "src/generators/workflow-value-descriptor-reference/constant-value-reference-pointer";
import { ExecutionCounterWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/execution-counter-workflow-reference-pointer";
import { NodeOutputWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/node-output-workflow-reference-pointer";
import { VellumSecretWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/vellum-secret-workflow-reference-pointer";
import { WorkflowInputReferencePointer } from "src/generators/workflow-value-descriptor-reference/workflow-input-reference-pointer";
import {
  IterableConfig,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export declare namespace WorkflowValueDescriptorReferencePointer {
  export interface Args {
    workflowContext: WorkflowContext;
    workflowValueReferencePointer: WorkflowValueDescriptorReferenceType;
    iterableConfig?: IterableConfig;
  }
}

export class WorkflowValueDescriptorReferencePointer extends AstNode {
  private workflowContext: WorkflowContext;
  public readonly workflowValueReferencePointer: WorkflowValueDescriptorReferenceType["type"];
  private iterableConfig?: IterableConfig;
  public astNode:
    | BaseNodeInputWorkflowReferencePointer<WorkflowValueDescriptorReferenceType>
    | undefined;

  constructor(args: WorkflowValueDescriptorReferencePointer.Args) {
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
    | BaseNodeInputWorkflowReferencePointer<WorkflowValueDescriptorReferenceType>
    | undefined {
    const referenceType = workflowValueReferencePointer.type;

    switch (referenceType) {
      case "NODE_OUTPUT": {
        const reference = new NodeOutputWorkflowReferencePointer({
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
        return new WorkflowInputReferencePointer({
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
        return new ConstantValueReferencePointer({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
          iterableConfig: this.iterableConfig,
        });
      case "VELLUM_SECRET":
        return new VellumSecretWorkflowReferencePointer({
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "EXECUTION_COUNTER":
        return new ExecutionCounterWorkflowReferencePointer({
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
