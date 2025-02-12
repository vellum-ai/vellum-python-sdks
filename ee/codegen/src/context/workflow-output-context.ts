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
  public readonly name: string;

  constructor({
    workflowContext,
    terminalNodeData,
    workflowOutputValue,
  }: WorkflowOutputContext.Args) {
    this.workflowContext = workflowContext;
    this.terminalNodeData = terminalNodeData;
    this.workflowOutputValue = workflowOutputValue;
    this.name = this.getOutputVariableName();
  }

  public getFinalOutputNodeData():
    | FinalOutputNodeType
    | WorkflowOutputValueType {
    if (this.workflowOutputValue) {
      return this.workflowOutputValue;
    } else if (this.terminalNodeData) {
      return this.terminalNodeData;
    } else {
      throw new WorkflowOutputGenerationError(
        "Expected either workflow output value or terminal node data to be defined"
      );
    }
  }

  public getWorkflowValueDescriptor(): WorkflowValueDescriptor {
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

  private getOutputVariableName(): string {
    if (this.terminalNodeData) {
      const outputVariable = this.workflowContext.getOutputVariableContextById(
        this.terminalNodeData.data.outputId
      );
      return outputVariable.name;
    } else if (this.workflowOutputValue) {
      const outputVariable = this.workflowContext.getOutputVariableContextById(
        this.workflowOutputValue.outputVariableId
      );
      return outputVariable.name;
    } else {
      throw new WorkflowOutputGenerationError(
        "Expected either workflow output value or terminal node data to be defined"
      );
    }
  }
}
