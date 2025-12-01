import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { vellumValue } from "src/codegen";
import { VELLUM_WORKFLOW_ROOT_MODULE_PATH } from "src/constants";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { NodeNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Json } from "src/generators/json";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  WorkflowSandboxDatasetRow,
  WorkflowSandboxDatasetRowMock,
  WorkflowSandboxInputs,
  WorkflowTrigger,
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
      initializer: new ListInstantiation(
        this.sandboxInputs.map((input, index) =>
          this.getWorkflowInput(input, index)
        ),
        { endWithComma: true }
      ),
    });
    this.inheritReferences(datasetField);

    const sandboxRunnerField = python.field({
      name: "runner",
      initializer: new ClassInstantiation({
        classReference: new Reference({
          name: "WorkflowSandboxRunner",
          modulePath:
            this.workflowContext.sdkModulePathNames.SANDBOX_RUNNER_MODULE_PATH,
        }),
        arguments_: [
          new MethodArgument({
            name: "workflow",
            value: new ClassInstantiation({
              classReference: new Reference({
                name: this.workflowContext.workflowClassName,
                modulePath: this.workflowContext.modulePath,
              }),
              arguments_: [],
            }),
          }),
          new MethodArgument({
            name: "dataset",
            value: new Reference({
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
  ): ClassInstantiation {
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
    const arguments_: MethodArgument[] = [
      new MethodArgument({
        name: "label",
        value: new StrInstantiation(label),
      }),
    ];

    // Determine which inputs belong to trigger attributes vs workflow inputs
    const triggers = this.workflowContext.triggers ?? [];
    const trigger = !isNil(workflowTriggerId)
      ? triggers.find((t) => t.id === workflowTriggerId)
      : undefined;

    // Build lookup maps for trigger attributes by both ID and key
    const triggerAttributesById = new Map(
      trigger?.attributes.map((attr) => [attr.id, attr]) ?? []
    );
    const triggerAttributesByKey = new Map(
      trigger?.attributes.map((attr) => [attr.key, attr]) ?? []
    );

    // Helper to check if an input is a trigger attribute input
    const isTriggerAttributeInput = (
      input: WorkflowSandboxInputs[number]
    ): boolean => {
      // Check by input_variable_id first (production format)
      if ("input_variable_id" in input && input.input_variable_id) {
        return triggerAttributesById.has(input.input_variable_id);
      }
      // Fallback to name matching (test format)
      if ("name" in input && input.name) {
        return triggerAttributesByKey.has(removeEscapeCharacters(input.name));
      }
      return false;
    };

    // Separate inputs into trigger attribute inputs and workflow inputs
    const workflowInputs = hasInputs
      ? inputs.filter((input) => !isTriggerAttributeInput(input))
      : [];

    // Add workflow inputs (excluding trigger attribute inputs)
    // Only name-based inputs can be workflow inputs
    const nameBasedWorkflowInputs = workflowInputs.filter(
      (input): input is WorkflowSandboxInputs[number] & { name: string } =>
        "name" in input && typeof input.name === "string"
    );

    if (nameBasedWorkflowInputs.length > 0) {
      const inputsInstance = new ClassInstantiation({
        classReference: new Reference({
          name: "Inputs",
          modulePath: getGeneratedInputsModulePath(this.workflowContext),
        }),
        arguments_: nameBasedWorkflowInputs
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

            return new MethodArgument({
              name: inputVariableContext.name,
              value: vellumValue({
                vellumValue: input,
              }),
            });
          })
          .filter((argument): argument is MethodArgument => !isNil(argument)),
      });

      arguments_.push(
        new MethodArgument({
          name: "inputs",
          value: inputsInstance,
        })
      );
    }

    if (!isNil(workflowTriggerId) && trigger) {
      // Filter inputs to only those that match trigger attributes for this specific trigger
      const triggerInputs = hasInputs
        ? inputs.filter(
            (input) => isTriggerAttributeInput(input) && !isNil(input.value)
          )
        : [];

      const triggerInstance = this.getTriggerInstance(
        trigger,
        triggerInputs,
        triggerAttributesById,
        triggerAttributesByKey
      );

      if (triggerInstance) {
        arguments_.push(
          new MethodArgument({
            name: "workflow_trigger",
            value: triggerInstance,
          })
        );
      }
    }

    if (!isNil(mocks) && mocks.length > 0) {
      const mockNodes = mocks
        .map((mock) => this.getMockNodeExecution(mock))
        .filter((node): node is ClassInstantiation => !isNil(node));

      if (mockNodes.length > 0) {
        const mocksArray = new ListInstantiation(mockNodes, {
          endWithComma: true,
        });

        arguments_.push(
          new MethodArgument({
            name: "mocks",
            value: mocksArray,
          })
        );
      }
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "DatasetRow",
        modulePath: ["vellum", "workflows", "inputs"],
      }),
      arguments_,
    });
  }

  private getMockNodeExecution(
    mock: WorkflowSandboxDatasetRowMock
  ): ClassInstantiation | null {
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

    const arguments_: MethodArgument[] = [];

    // Generate when_condition using WorkflowValueDescriptor
    if (!isNil(mock.when_condition)) {
      const whenConditionAst = new WorkflowValueDescriptor({
        workflowValueDescriptor: mock.when_condition,
        workflowContext: this.workflowContext,
      });

      arguments_.push(
        new MethodArgument({
          name: "when_condition",
          value: whenConditionAst,
        })
      );
    }

    // Generate then_outputs by instantiating the node's Outputs class
    const outputsArguments: MethodArgument[] = Object.entries(
      mock.then_outputs
    ).map(
      ([key, value]) =>
        new MethodArgument({
          name: key,
          value: new Json(value),
        })
    );

    const thenOutputsInstance = new ClassInstantiation({
      classReference: new Reference({
        name: nodeContext.nodeClassName,
        modulePath: nodeContext.nodeModulePath,
        attribute: ["Outputs"],
      }),
      arguments_: outputsArguments,
    });

    arguments_.push(
      new MethodArgument({
        name: "then_outputs",
        value: thenOutputsInstance,
      })
    );

    return new ClassInstantiation({
      classReference: new Reference({
        name: "MockNodeExecution",
        modulePath: VELLUM_WORKFLOW_ROOT_MODULE_PATH,
      }),
      arguments_,
    });
  }

  private getTriggerInstance(
    trigger: WorkflowTrigger,
    triggerInputs: WorkflowSandboxInputs,
    triggerAttributesById: Map<string, WorkflowTrigger["attributes"][number]>,
    triggerAttributesByKey: Map<string, WorkflowTrigger["attributes"][number]>
  ): ClassInstantiation {
    const triggerClassInfo = getTriggerClassInfo(trigger, this.workflowContext);

    // Generate arguments for the trigger instance from the pre-filtered inputs
    const arguments_: MethodArgument[] = triggerInputs
      .map((input) => {
        // Resolve the attribute to get the correct key name
        let attr: WorkflowTrigger["attributes"][number] | undefined;

        // Check by input_variable_id first (production format)
        if ("input_variable_id" in input && input.input_variable_id) {
          attr = triggerAttributesById.get(input.input_variable_id);
        }

        // Fallback to name matching (test format)
        if (!attr && "name" in input && input.name) {
          attr = triggerAttributesByKey.get(removeEscapeCharacters(input.name));
        }

        if (!attr) {
          return null;
        }

        return new MethodArgument({
          name: attr.key,
          value: vellumValue({ vellumValue: input }),
        });
      })
      .filter((arg): arg is MethodArgument => arg !== null);

    return new ClassInstantiation({
      classReference: new Reference({
        name: triggerClassInfo.className,
        modulePath: triggerClassInfo.modulePath,
      }),
      arguments_,
    });
  }
}
