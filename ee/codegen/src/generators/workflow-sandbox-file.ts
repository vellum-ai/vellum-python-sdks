import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { isNil } from "lodash";

import { vellumValue } from "src/codegen";
import { VELLUM_WORKFLOW_ROOT_MODULE_PATH } from "src/constants";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { NodeNotFoundError } from "src/generators/errors";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  WorkflowSandboxDatasetRow,
  WorkflowSandboxDatasetRowMock,
  WorkflowSandboxInputs,
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
      const mockNodes = mocks
        .map((mock) => this.getMockNodeExecution(mock))
        .filter((node): node is python.ClassInstantiation => !isNil(node));

      if (mockNodes.length > 0) {
        const mocksArray = python.TypeInstantiation.list(mockNodes, {
          endWithComma: true,
        });

        arguments_.push(
          python.methodArgument({
            name: "mocks",
            value: mocksArray,
          })
        );
      }
    }

    return python.instantiateClass({
      classReference: python.reference({
        name: "DatasetRow",
        modulePath: ["vellum", "workflows", "inputs"],
      }),
      arguments_,
    });
  }

  private getMockNodeExecution(
    mock: WorkflowSandboxDatasetRowMock
  ): python.ClassInstantiation | null {
    const nodeContext = this.workflowContext.findNodeContext(mock.node_id);

    if (!nodeContext) {
      this.workflowContext.addError(
        new NodeNotFoundError(
          `Failed to generate mock for node_id '${mock.node_id}' because node context was not found`,
          "WARNING"
        )
      );
      return null;
    }

    const arguments_: python.MethodArgument[] = [];

    // Generate when_condition using WorkflowValueDescriptor
    if (!isNil(mock.when_condition)) {
      const whenConditionAst = new WorkflowValueDescriptor({
        workflowValueDescriptor: mock.when_condition,
        workflowContext: this.workflowContext,
      });

      arguments_.push(
        python.methodArgument({
          name: "when_condition",
          value: whenConditionAst,
        })
      );
    }

    // Generate then_outputs by instantiating the node's Outputs class
    const outputsArguments: python.MethodArgument[] = Object.entries(
      mock.then_outputs
    ).map(([key, value]) =>
      python.methodArgument({
        name: key,
        value: python.TypeInstantiation.str(String(value)),
      })
    );

    const thenOutputsInstance = python.instantiateClass({
      classReference: python.reference({
        name: nodeContext.nodeClassName,
        modulePath: nodeContext.nodeModulePath,
        attribute: ["Outputs"],
      }),
      arguments_: outputsArguments,
    });

    arguments_.push(
      python.methodArgument({
        name: "then_outputs",
        value: thenOutputsInstance,
      })
    );

    return python.instantiateClass({
      classReference: python.reference({
        name: "MockNodeExecution",
        modulePath: VELLUM_WORKFLOW_ROOT_MODULE_PATH,
      }),
      arguments_,
    });
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
