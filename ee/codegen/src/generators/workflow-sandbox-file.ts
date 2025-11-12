import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { vellumValue } from "src/codegen";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import {
  WorkflowSandboxInputs,
  WorkflowSandboxDatasetRow,
} from "src/types/vellum";
import { removeEscapeCharacters } from "src/utils/casing";
import { getGeneratedInputsModulePath } from "src/utils/paths";

export declare namespace WorkflowSandboxFile {
  interface Args extends BasePersistedFile.Args {
    sandboxInputs: WorkflowSandboxDatasetRow[];
  }
}

export class WorkflowSandboxFile extends BasePersistedFile {
  private readonly sandboxInputs: WorkflowSandboxDatasetRow[];

  public constructor({
    workflowContext,
    sandboxInputs,
  }: WorkflowSandboxFile.Args) {
    super({ workflowContext });
    this.sandboxInputs = sandboxInputs;
  }

  protected getModulePath(): string[] {
    return [...this.workflowContext.modulePath.slice(0, -1), "sandbox"];
  }

  protected getFileStatements(): AstNode[] {
    const datasetField = python.field({
      name: "dataset",
      initializer: python.TypeInstantiation.list(
        this.sandboxInputs.map((input, index) =>
          this.getWorkflowInput(input, index)
        ),
        { endWithComma: true }
      ),
    });
    this.inheritReferences(datasetField);

    const sandboxRunnerField = python.field({
      name: "runner",
      initializer: python.instantiateClass({
        classReference: python.reference({
          name: "WorkflowSandboxRunner",
          modulePath:
            this.workflowContext.sdkModulePathNames.SANDBOX_RUNNER_MODULE_PATH,
        }),
        arguments_: [
          python.methodArgument({
            name: "workflow",
            value: python.instantiateClass({
              classReference: python.reference({
                name: this.workflowContext.workflowClassName,
                modulePath: this.workflowContext.modulePath,
              }),
              arguments_: [],
            }),
          }),
          python.methodArgument({
            name: "dataset",
            value: python.reference({
              name: "dataset",
            }),
          }),
        ],
      }),
    });
    this.inheritReferences(sandboxRunnerField);

    return [
      datasetField,
      sandboxRunnerField,
      // Using code block instead of method invocation since the latter tries to import `runner.run` after
      // specifying as a reference, even though it's a locally defined variable.
      python.codeBlock(`\
if __name__ == "__main__":
    runner.run()
`),
    ];
  }

  private getWorkflowInput(
    row: WorkflowSandboxDatasetRow,
    index: number
  ): python.ClassInstantiation {
    const inputs: WorkflowSandboxInputs = Array.isArray(row)
      ? row
      : "inputs" in row
      ? row.inputs
      : [];
    const label: string = Array.isArray(row)
      ? `Example ${index + 1}`
      : row.label;
    const workflowTriggerId: string | undefined = Array.isArray(row)
      ? undefined
      : row.workflow_trigger_id;

    const hasInputs = inputs.length > 0;
    const arguments_: python.MethodArgument[] = [
      python.methodArgument({
        name: "label",
        value: python.TypeInstantiation.str(label),
      }),
    ];

    if (hasInputs) {
      const inputsInstance = python.instantiateClass({
        classReference: python.reference({
          name: "Inputs",
          modulePath: getGeneratedInputsModulePath(this.workflowContext),
        }),
        arguments_: inputs
          .map((input) => {
            if (isNil(input.value)) {
              return null;
            }

            const rawName = removeEscapeCharacters(input.name);
            const inputVariableContext =
              this.workflowContext.findInputVariableContextByRawName(rawName);

            if (isNil(inputVariableContext)) {
              return null;
            }

            return python.methodArgument({
              name: inputVariableContext.name,
              value: vellumValue({
                vellumValue: input,
              }),
            });
          })
          .filter(
            (argument): argument is python.MethodArgument => !isNil(argument)
          ),
      });

      arguments_.push(
        python.methodArgument({
          name: "inputs",
          value: inputsInstance,
        })
      );
    }

    if (!isNil(workflowTriggerId)) {
      arguments_.push(
        python.methodArgument({
          name: "workflow_trigger_id",
          value: python.TypeInstantiation.uuid(workflowTriggerId),
        })
      );
    }

    return python.instantiateClass({
      classReference: python.reference({
        name: "DatasetRow",
        modulePath: ["vellum", "workflows", "inputs"],
      }),
      arguments_,
    });
  }
}
