import { ArrayWorkflowReference } from "./array-workflow-reference";
import { DictionaryWorkflowReference } from "./dictionary-workflow-reference";
import { WorkflowStateReference } from "./workflow-state-reference";

import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import { ConstantValueReference } from "src/generators/workflow-value-descriptor-reference/constant-value-reference";
import { EnvironmentVariableWorkflowReference } from "src/generators/workflow-value-descriptor-reference/environment-variable-workflow-reference";
import { ExecutionCounterWorkflowReference } from "src/generators/workflow-value-descriptor-reference/execution-counter-workflow-reference";
import { NodeOutputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/node-output-workflow-reference";
import { TriggerAttributeWorkflowReference } from "src/generators/workflow-value-descriptor-reference/trigger-attribute-workflow-reference";
import { VellumSecretWorkflowReference } from "src/generators/workflow-value-descriptor-reference/vellum-secret-workflow-reference";
import { WorkflowInputReference } from "src/generators/workflow-value-descriptor-reference/workflow-input-reference";
import {
  AttributeConfig,
  IterableConfig,
  WorkflowDataNode,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export declare namespace WorkflowValueDescriptorReference {
  export interface Args {
    nodeContext?: BaseNodeContext<WorkflowDataNode>;
    workflowContext: WorkflowContext;
    workflowValueReferencePointer: WorkflowValueDescriptorReferenceType;
    iterableConfig?: IterableConfig;
    attributeConfig?: AttributeConfig;
  }
}

export class WorkflowValueDescriptorReference extends AstNode {
  private nodeContext?: BaseNodeContext<WorkflowDataNode>;
  private workflowContext: WorkflowContext;
  public readonly workflowValueReferencePointer: WorkflowValueDescriptorReferenceType["type"];
  private iterableConfig?: IterableConfig;
  private attributeConfig?: AttributeConfig;
  public astNode:
    | BaseNodeInputWorkflowReference<WorkflowValueDescriptorReferenceType>
    | undefined;

  constructor(args: WorkflowValueDescriptorReference.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.workflowContext = args.workflowContext;
    this.nodeContext = args.nodeContext;
    this.workflowValueReferencePointer =
      args.workflowValueReferencePointer.type;
    this.iterableConfig = args.iterableConfig;
    this.attributeConfig = args.attributeConfig;

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
          nodeContext: this.nodeContext,
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
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "WORKFLOW_STATE":
        return new WorkflowStateReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "CONSTANT_VALUE":
        return new ConstantValueReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
          iterableConfig: this.iterableConfig,
          attributeConfig: this.attributeConfig,
        });
      case "VELLUM_SECRET":
        return new VellumSecretWorkflowReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "ENVIRONMENT_VARIABLE":
        return new EnvironmentVariableWorkflowReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "EXECUTION_COUNTER":
        return new ExecutionCounterWorkflowReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "TRIGGER_ATTRIBUTE": {
        const reference = new TriggerAttributeWorkflowReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
        if (reference.getAstNode()) {
          return reference;
        } else {
          return undefined;
        }
      }
      case "DICTIONARY_REFERENCE":
        return new DictionaryWorkflowReference({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          nodeInputWorkflowReferencePointer: workflowValueReferencePointer,
        });
      case "ARRAY_REFERENCE":
        return new ArrayWorkflowReference({
          nodeContext: this.nodeContext,
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
