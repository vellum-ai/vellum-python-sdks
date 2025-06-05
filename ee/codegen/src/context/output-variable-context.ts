import { isNil, isEmpty } from "lodash";
import { VellumVariable } from "vellum-ai/api/types";

import { WorkflowContext } from "src/context/workflow-context";
import { toValidPythonIdentifier } from "src/utils/casing";

export declare namespace OutputVariableContext {
  export type Args = {
    outputVariableData: VellumVariable;
    workflowContext: WorkflowContext;
  };
}

export class OutputVariableContext {
  private readonly workflowContext: WorkflowContext;
  private readonly outputVariableData: VellumVariable;
  public readonly name: string;

  constructor({
    outputVariableData,
    workflowContext,
  }: OutputVariableContext.Args) {
    this.workflowContext = workflowContext;
    this.outputVariableData = outputVariableData;
    this.name = this.generateSanitizedOutputVariableName();
  }

  public getOutputVariableId(): string {
    return this.outputVariableData.id;
  }

  public getOutputVariableData(): VellumVariable {
    return this.outputVariableData;
  }

  public getRawName(): string {
    return this.outputVariableData.key;
  }

  private generateSanitizedOutputVariableName(): string {
    const defaultName = "output_";

    const rawOutputVariableName = this.outputVariableData.key;
    const initialOutputVariableName =
      !isNil(rawOutputVariableName) && !isEmpty(rawOutputVariableName)
        ? toValidPythonIdentifier(rawOutputVariableName, "output")
        : defaultName;

    // Deduplicate the output variable name if it's already in use
    let sanitizedName = initialOutputVariableName;
    let numRenameAttempts = 0;
    while (this.workflowContext.isOutputVariableNameUsed(sanitizedName)) {
      sanitizedName = `${initialOutputVariableName}${
        initialOutputVariableName.endsWith("_") ? "" : "_"
      }${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }

    return sanitizedName;
  }
}
