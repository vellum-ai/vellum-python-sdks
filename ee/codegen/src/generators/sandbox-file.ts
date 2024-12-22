import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BasePersistedFile } from "./base-persisted-file";
import { python } from "@fern-api/python-ast";
import type { WorkflowFile } from "./workflow";
import type { Inputs } from "./inputs";

export declare namespace SandboxFile {
  interface Args extends BasePersistedFile.Args {
    workflowFile: WorkflowFile;
    inputsFile: Inputs;
    sandboxInputs: Record<string, unknown>[];
  }
}

export class SandboxFile extends BasePersistedFile {
  private readonly workflowFile: WorkflowFile;
  private readonly inputsFile: Inputs;
  private readonly sandboxInputs: Record<string, unknown>[];

  public constructor({
    workflowContext,
    workflowFile,
    inputsFile,
    sandboxInputs,
  }: SandboxFile.Args) {
    super({ workflowContext });
    this.workflowFile = workflowFile;
    this.inputsFile = inputsFile;
    this.sandboxInputs = sandboxInputs;
  }

  protected getModulePath(): string[] {
    return [this.workflowContext.moduleName, "sandbox"];
  }

  protected getFileStatements(): AstNode[] {
    const sandboxRunnerField = python.field({
      name: "runner",
      initializer: python.instantiateClass({
        classReference: python.reference({
          name: "SandboxRunner",
          modulePath:
            this.workflowContext.sdkModulePathNames.SANDBOX_RUNNER_MODULE_PATH,
        }),
        arguments_: [
          python.methodArgument({
            name: "workflow",
            value: python.reference({
              name: "Workflow",
              modulePath: this.workflowFile.getModulePath(),
            }),
          }),
          python.methodArgument({
            name: "inputs",
            value: python.TypeInstantiation.list(
              this.sandboxInputs.map((input) => this.getWorkflowInput(input))
            ),
          }),
        ],
      }),
    });
    this.inheritReferences(sandboxRunnerField);

    return [
      python.codeBlock(`\
if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")
        `),
      sandboxRunnerField,
      python.codeBlock("runner.run()"),
    ];
  }

  private getWorkflowInput(
    input: Record<string, unknown>
  ): python.ClassInstantiation {
    return python.instantiateClass({
      classReference: python.reference({
        name: "Inputs",
        modulePath: this.inputsFile.getModulePath(),
      }),
      arguments_: Object.entries(input).map(([key, value]) =>
        python.methodArgument({
          name: key,
          value: this.getWorkflowInputValue(value),
        })
      ),
    });
  }

  private getWorkflowInputValue(value: unknown): python.TypeInstantiation {
    if (typeof value === "string") {
      return python.TypeInstantiation.str(value);
    }
    if (typeof value === "number") {
      return python.TypeInstantiation.float(value);
    }
    if (typeof value === "boolean") {
      return python.TypeInstantiation.bool(value);
    }
    if (Array.isArray(value)) {
      return python.TypeInstantiation.list(
        value.map(this.getWorkflowInputValue)
      );
    }
    if (value === null) {
      return python.TypeInstantiation.none();
    }
    return python.TypeInstantiation.dict(JSON.parse(JSON.stringify(value)));
  }
}
