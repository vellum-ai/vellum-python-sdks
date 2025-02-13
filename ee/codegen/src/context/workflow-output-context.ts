import { isEmpty, isNil } from "lodash";

import { WorkflowContext } from "src/context/workflow-context";
import { WorkflowOutputGenerationError } from "src/generators/errors";
import {
  FinalOutputNode as FinalOutputNodeType,
  WorkflowOutputValue as WorkflowOutputValueType,
} from "src/types/vellum";
import { toPythonSafeSnakeCase } from "src/utils/casing";
import { getNodeIdFromNodeOutputWorkflowReference } from "src/utils/nodes";

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
    terminalNodeData,
    workflowContext,
    workflowOutputValue,
  }: WorkflowOutputContext.Args) {
    this.workflowContext = workflowContext;
    this.terminalNodeData = terminalNodeData;
    this.workflowOutputValue = workflowOutputValue;
    this.name = this.generateSanitizedOutputVariableName();
  }

  public getOutputNodeId(): string {
    let outputNodeId: string | undefined;
    if (this.workflowOutputValue) {
      outputNodeId = getNodeIdFromNodeOutputWorkflowReference(
        this.workflowOutputValue
      );
    }
    if (this.terminalNodeData) {
      outputNodeId = this.terminalNodeData.id;
    }

    if (!outputNodeId) {
      throw new WorkflowOutputGenerationError(
        "Expected output node id in either output values or terminal data"
      );
    }
    return outputNodeId;
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

  private generateSanitizedOutputVariableName(): string {
    const defaultName = "output_";

    let rawOutputVariableName: string;
    if (this.terminalNodeData) {
      rawOutputVariableName = this.terminalNodeData.data.name;
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

    return !isNil(rawOutputVariableName) && !isEmpty(rawOutputVariableName)
      ? toPythonSafeSnakeCase(rawOutputVariableName, "output")
      : defaultName;
  }
}
