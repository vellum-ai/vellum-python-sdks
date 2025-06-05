import { isEmpty, isNil } from "lodash";
import { CodeResourceDefinition, VellumVariable } from "vellum-ai/api/types";

import { WorkflowContext } from "src/context/workflow-context";
import {
  removeEscapeCharacters,
  toValidPythonIdentifier,
} from "src/utils/casing";
import { getGeneratedStateModulePath } from "src/utils/paths";

export declare namespace StateVariableContext {
  export type Args = {
    stateVariableData: VellumVariable;
    workflowContext: WorkflowContext;
  };
}

export class StateVariableContext {
  private readonly workflowContext: WorkflowContext;
  private readonly stateVariableData: VellumVariable;
  public readonly definition: CodeResourceDefinition;

  public readonly name: string;

  constructor({
    stateVariableData,
    workflowContext,
  }: StateVariableContext.Args) {
    this.workflowContext = workflowContext;
    this.stateVariableData = stateVariableData;
    this.definition = {
      name: "State",
      module: getGeneratedStateModulePath(workflowContext),
    };

    this.name = this.generateSanitizedStateVariableName();
  }

  public getStateVariableId(): string {
    return this.stateVariableData.id;
  }

  public getStateVariableData(): VellumVariable {
    return this.stateVariableData;
  }

  public getRawName(): string {
    // This is for an edge case where there are escape characters in the variable
    return removeEscapeCharacters(this.stateVariableData.key);
  }

  private generateSanitizedStateVariableName(): string {
    const defaultName = "state_";
    const rawStateVariableName = this.stateVariableData.key;

    const initialStateVariableName =
      !isNil(rawStateVariableName) && !isEmpty(rawStateVariableName)
        ? toValidPythonIdentifier(rawStateVariableName, "state")
        : defaultName;

    // Deduplicate the state variable name if it's already in use
    let sanitizedName = initialStateVariableName;
    let numRenameAttempts = 0;
    while (this.workflowContext.isStateVariableNameUsed(sanitizedName)) {
      sanitizedName = `${initialStateVariableName}${
        initialStateVariableName.endsWith("_") ? "" : "_"
      }${numRenameAttempts + 1}`;
      numRenameAttempts += 1;
    }

    return sanitizedName;
  }
}
