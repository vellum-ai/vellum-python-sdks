import { isEmpty, isNil } from "lodash";
import { CodeResourceDefinition, VellumVariable } from "vellum-ai/api/types";

import { WorkflowContext } from "src/context/workflow-context";
import {
  removeEscapeCharacters,
  toValidPythonIdentifier,
} from "src/utils/casing";
import { getGeneratedInputsModulePath } from "src/utils/paths";

export declare namespace InputVariableContext {
  export type Args = {
    inputVariableData: VellumVariable;
    workflowContext: WorkflowContext;
  };
}

export class InputVariableContext {
  private readonly workflowContext: WorkflowContext;
  private readonly inputVariableData: VellumVariable;
  public readonly definition: CodeResourceDefinition;

  public readonly name: string;

  constructor({
    inputVariableData,
    workflowContext,
  }: InputVariableContext.Args) {
    this.workflowContext = workflowContext;
    this.inputVariableData = inputVariableData;
    this.definition = {
      name: "Inputs",
      module: getGeneratedInputsModulePath(workflowContext),
    };

    this.name = this.generateSanitizedInputVariableName();
  }

  public getInputVariableId(): string {
    return this.inputVariableData.id;
  }

  public getInputVariableData(): VellumVariable {
    return this.inputVariableData;
  }

  public getRawName(): string {
    // This is for an edge case where there are escape characters in the variable
    return removeEscapeCharacters(this.inputVariableData.key);
  }

  private generateSanitizedInputVariableName(): string {
    const defaultName = "input_";
    const rawInputVariableName = this.inputVariableData.key;

    const initialInputVariableName =
      !isNil(rawInputVariableName) && !isEmpty(rawInputVariableName)
        ? toValidPythonIdentifier(rawInputVariableName, "input")
        : defaultName;

    // Deduplicate the input variable name if it's already in use
    let sanitizedName = initialInputVariableName;
    let numRenameAttempts = 0;
    while (this.workflowContext.isInputVariableNameUsed(sanitizedName)) {
      sanitizedName = `${initialInputVariableName}${
        initialInputVariableName.endsWith("_") ? "" : "_"
      }${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }

    return sanitizedName;
  }
}
