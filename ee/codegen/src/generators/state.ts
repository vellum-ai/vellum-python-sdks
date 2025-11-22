import { python } from "@fern-api/python-ast";
import { isEqual } from "lodash";

import { BasePersistedFile } from "./base-persisted-file";
import { BaseState } from "./base-state";
import { Class } from "./extensions/class";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { getGeneratedStateModulePath } from "src/utils/paths";

export declare namespace State {
  interface Args {
    workflowContext: WorkflowContext;
  }
}

export class State extends BasePersistedFile {
  public readonly baseStateClassReference: python.Reference;
  public readonly stateClass: Class | undefined;

  constructor({ workflowContext }: State.Args) {
    super({ workflowContext: workflowContext });
    this.baseStateClassReference = new BaseState({ workflowContext });

    this.stateClass = this.generateStateClass();
  }

  getModulePath(): string[] {
    return getGeneratedStateModulePath(this.workflowContext);
  }

  public getFileStatements() {
    if (!this.stateClass) {
      return;
    }
    return [this.stateClass];
  }

  private generateStateClass(): Class | undefined {
    const stateVariableContextsById =
      this.workflowContext.stateVariableContextsById;

    // Filter down to only those input variables that belong to the same directory as the workflow module.
    const stateVariables = Array.from(
      [...stateVariableContextsById.values()].filter((stateVariableContext) => {
        return isEqual(
          stateVariableContext.definition.module.slice(0, -1),
          this.workflowContext.modulePath.slice(0, -1)
        );
      })
    );

    const [firstStateVariableContext] = stateVariables;
    if (!firstStateVariableContext) {
      return;
    }

    const stateClass = new Class({
      name: firstStateVariableContext.definition.name,
      extends_: [this.baseStateClassReference],
    });
    this.addReference(this.baseStateClassReference);

    stateVariables.forEach((stateVariableContext) => {
      const stateVariableData = stateVariableContext.getStateVariableData();
      const stateVariableName = stateVariableContext.name;
      const vellumVariableField = codegen.vellumVariable({
        variable: {
          id: stateVariableData.id,
          // Use the sanitized name from the input variable context to ensure it's a valid
          // attribute name (as opposed to the raw name from the input variable data).
          name: stateVariableName,
          type: stateVariableData.type,
          required: stateVariableData.required,
          default: stateVariableData.default,
        },
        defaultRequired: false,
      });

      stateClass.add(vellumVariableField);
    });

    return stateClass;
  }

  public async persist(): Promise<void> {
    if (!this.stateClass) {
      return;
    }
    super.persist();
  }
}
