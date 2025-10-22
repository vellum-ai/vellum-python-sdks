import { OutputVariableContext } from "./output-variable-context";

import { WorkflowContext } from "src/context/workflow-context";
import { WorkflowOutputGenerationError } from "src/generators/errors";
import {
  FinalOutputNode as FinalOutputNodeType,
  WorkflowOutputValue as WorkflowOutputValueType,
  WorkflowValueDescriptor,
} from "src/types/vellum";

export declare namespace WorkflowOutputContext {
  export type Args = {
    workflowContext: WorkflowContext;
    terminalNodeData?: FinalOutputNodeType;
    workflowOutputValue?: WorkflowOutputValueType;
  };
}

export class WorkflowOutputContext {
  private readonly workflowContext: WorkflowContext;
  private readonly terminalNodeData?: FinalOutputNodeType;
  private readonly workflowOutputValue?: WorkflowOutputValueType;

  constructor({
    workflowContext,
    terminalNodeData,
    workflowOutputValue,
  }: WorkflowOutputContext.Args) {
    this.workflowContext = workflowContext;
    this.terminalNodeData = terminalNodeData;
    this.workflowOutputValue = workflowOutputValue;
  }

  private getOutputVariableId(): string {
    if (this.workflowOutputValue) {
      return this.workflowOutputValue.outputVariableId;
    } else if (this.terminalNodeData) {
      return this.terminalNodeData.data.outputId;
    } else {
      throw new WorkflowOutputGenerationError(
        "Expected either workflow output value or terminal node data to be defined"
      );
    }
  }

  public getWorkflowValueDescriptor(): WorkflowValueDescriptor | undefined {
    if (this.workflowOutputValue) {
      return this.workflowOutputValue.value;
    } else if (this.terminalNodeData) {
      return {
        type: "NODE_OUTPUT",
        nodeId: this.terminalNodeData.id,
        nodeOutputId: this.terminalNodeData.data.outputId,
      };
    } else {
      throw new WorkflowOutputGenerationError(
        "Expected workflow output value or terminal node data to be defined"
      );
    }
  }

  public getOutputVariable(): OutputVariableContext | undefined {
    const outputVariableId = this.getOutputVariableId();
    return this.workflowContext.getOutputVariableContextById(outputVariableId);
  }
}
