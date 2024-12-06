import { python } from "@fern-api/python-ast";
import { isEqual } from "lodash";

import { BasePersistedFile } from "./base-persisted-file";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { getGeneratedInputsModulePath } from "src/utils/paths";

export declare namespace Inputs {
  interface Args {
    workflowContext: WorkflowContext;
    name?: string;
  }
}

export class Inputs extends BasePersistedFile {
  public readonly baseInputsClassReference: python.Reference;
  public readonly inputsClass: python.Class | undefined;

  constructor({ name, workflowContext }: Inputs.Args) {
    super({ workflowContext: workflowContext });
    this.baseInputsClassReference = python.reference({
      name: "BaseInputs",
      modulePath: workflowContext.sdkModulePathNames.INPUTS_MODULE_PATH,
    });

    this.inputsClass = this.generateInputsClass({
      name,
    });
  }

  getModulePath(): string[] {
    return getGeneratedInputsModulePath(this.workflowContext);
  }

  public getFileStatements() {
    if (!this.inputsClass) {
      return;
    }
    return [this.inputsClass];
  }

  private generateInputsClass({
    name,
  }: {
    name: string | undefined;
  }): python.Class | undefined {
    const inputVariableContextsById =
      this.workflowContext.inputVariableContextsById;

    // Filter down to only those input variables that belong to the same directory as the workflow module.
    const inputVariables = Array.from(
      [...inputVariableContextsById.values()].filter((inputVariableContext) => {
        return isEqual(
          inputVariableContext.modulePath.slice(0, -1),
          this.workflowContext.modulePath.slice(0, -1)
        );
      })
    );

    if (inputVariables.length === 0) {
      return;
    }

    const inputsClassName = name ?? "Inputs";
    const inputsClass = python.class_({
      name: inputsClassName,
      extends_: [this.baseInputsClassReference],
    });
    this.addReference(this.baseInputsClassReference);

    inputVariables.forEach((inputVariableContext) => {
      const inputVariableData = inputVariableContext.getInputVariableData();
      const inputVariableName = inputVariableContext.getInputVariableName();
      const vellumVariableField = codegen.vellumVariable({
        variable: {
          id: inputVariableData.id,
          name: inputVariableName,
          type: inputVariableData.type,
          required: inputVariableData.required,
          default: inputVariableData.default,
          extensions: inputVariableData.extensions,
        },
      });

      inputsClass.add(vellumVariableField);
    });

    return inputsClass;
  }

  public async persist(): Promise<void> {
    if (!this.inputsClass) {
      return;
    }
    super.persist();
  }
}
