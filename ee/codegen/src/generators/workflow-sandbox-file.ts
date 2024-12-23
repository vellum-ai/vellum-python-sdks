import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { vellumValue } from "src/codegen";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { WorkflowSandboxInputs } from "src/types/vellum";
import { getGeneratedInputsModulePath } from "src/utils/paths";

export declare namespace WorkflowSandboxFile {
  interface Args extends BasePersistedFile.Args {
    sandboxInputs: WorkflowSandboxInputs[];
  }
}

export class WorkflowSandboxFile extends BasePersistedFile {
  private readonly sandboxInputs: WorkflowSandboxInputs[];

  public constructor({
    workflowContext,
    sandboxInputs,
  }: WorkflowSandboxFile.Args) {
    super({ workflowContext });
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
              modulePath: this.workflowContext.modulePath,
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

    const runMethodInvocation = python.invokeMethod({
      methodReference: python.reference({
        name: "runner.run",
      }),
      arguments_: [],
    });

    return [
      python.codeBlock(`\
if __name__ != "__main__":
    raise Exception("This file is not meant to be imported")
`),
      sandboxRunnerField,
      runMethodInvocation,
    ];
  }

  private getWorkflowInput(
    inputs: WorkflowSandboxInputs
  ): python.ClassInstantiation {
    return python.instantiateClass({
      classReference: python.reference({
        name: "Inputs",
        modulePath: getGeneratedInputsModulePath(this.workflowContext),
      }),
      arguments_: inputs.map((input) =>
        python.methodArgument({
          name: input.name,
          value: vellumValue({
            vellumValue: input,
          }),
        })
      ),
    });
  }
}
