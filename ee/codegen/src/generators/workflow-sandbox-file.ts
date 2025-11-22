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
import { getTriggerClassInfo } from "src/utils/triggers";

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
    const mocks = Array.isArray(row)
      ? undefined
      : "mocks" in row
      ? row.mocks
      : undefined;

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
      const triggerReference = this.getTriggerReference(workflowTriggerId);

      if (triggerReference) {
        arguments_.push(
          python.methodArgument({
            name: "trigger",
            value: triggerReference,
          })
        );
      }
    }

    if (!isNil(mocks) && mocks.length > 0) {
      const mocksArray = python.TypeInstantiation.list(
        mocks.map((mock) => this.getMockDict(mock)),
        { endWithComma: true }
      );

      arguments_.push(
        python.methodArgument({
          name: "mocks",
          value: mocksArray,
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

  private getMockDict(
    mock: import("src/types/vellum").WorkflowSandboxDatasetRowMock
  ): python.AstNode {
    const entries: Array<{ key: python.AstNode; value: python.AstNode }> = [];

    // Add node_id
    entries.push({
      key: python.TypeInstantiation.str("node_id"),
      value: python.TypeInstantiation.str(mock.node_id),
    });

    // Add when_condition if present
    if (!isNil(mock.when_condition)) {
      entries.push({
        key: python.TypeInstantiation.str("when_condition"),
        value: this.jsonToPython(mock.when_condition),
      });
    }

    // Add then_outputs
    entries.push({
      key: python.TypeInstantiation.str("then_outputs"),
      value: this.jsonToPython(mock.then_outputs),
    });

    return python.TypeInstantiation.dict(entries);
  }

  private jsonToPython(value: unknown): python.AstNode {
    if (value === null || value === undefined) {
      return python.codeBlock("None");
    }
    if (typeof value === "boolean") {
      return python.codeBlock(value ? "True" : "False");
    }
    if (typeof value === "number") {
      return python.codeBlock(String(value));
    }
    if (typeof value === "string") {
      return python.TypeInstantiation.str(value);
    }
    if (Array.isArray(value)) {
      return python.TypeInstantiation.list(
        value.map((item) => this.jsonToPython(item))
      );
    }
    if (typeof value === "object") {
      const entries = Object.entries(value).map(([key, val]) => ({
        key: python.TypeInstantiation.str(key),
        value: this.jsonToPython(val),
      }));
      return python.TypeInstantiation.dict(entries);
    }
    return python.codeBlock("None");
  }

  private getTriggerReference(
    workflowTriggerId: string
  ): python.Reference | undefined {
    const triggerContext =
      this.workflowContext.findTriggerContext(workflowTriggerId);

    if (triggerContext) {
      return python.reference({
        name: triggerContext.triggerClassName,
        modulePath: triggerContext.triggerModulePath,
      });
    }

    const triggers = this.workflowContext.triggers ?? [];
    const trigger = triggers.find((t) => t.id === workflowTriggerId);

    if (!trigger) {
      return undefined;
    }

    const triggerClassInfo = getTriggerClassInfo(trigger, this.workflowContext);

    return python.reference({
      name: triggerClassInfo.className,
      modulePath: triggerClassInfo.modulePath,
    });
  }
}
