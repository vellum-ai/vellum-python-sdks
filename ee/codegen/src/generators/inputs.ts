import { python } from "@fern-api/python-ast";
import { isEqual } from "lodash";

import { BasePersistedFile } from "./base-persisted-file";
import { Class } from "./extensions/class";

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
  public readonly inputsClass: Class | undefined;

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
  }): Class | undefined {
    const inputVariableContextsById =
      this.workflowContext.inputVariableContextsById;

    // Filter down to only those input variables that belong to the same directory as the workflow module.
    const inputVariables = Array.from(
      [...inputVariableContextsById.values()].filter((inputVariableContext) => {
        return isEqual(
          inputVariableContext.definition.module.slice(0, -1),
          this.workflowContext.modulePath.slice(0, -1)
        );
      })
    );

    if (inputVariables.length === 0) {
      return;
    }

    const inputsClassName = name ?? "Inputs";
    const inputsClass = new Class({
      name: inputsClassName,
      extends_: [this.baseInputsClassReference],
    });
    this.addReference(this.baseInputsClassReference);

    inputVariables.forEach((inputVariableContext) => {
      const inputVariableData = inputVariableContext.getInputVariableData();
      const inputVariableName = inputVariableContext.name;
      const vellumVariableField = codegen.vellumVariable({
        variable: {
          id: inputVariableData.id,
          // Use the sanitized name from the input variable context to ensure it's a valid
          // attribute name (as opposed to the raw name from the input variable data).
          name: inputVariableName,
          type: inputVariableData.type,
          required: inputVariableData.required,
          default: inputVariableData.default,
        },
        defaultRequired: false,
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
