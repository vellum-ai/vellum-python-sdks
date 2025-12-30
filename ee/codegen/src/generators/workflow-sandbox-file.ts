import { isNil } from "lodash";

import { vellumValue } from "src/codegen";
import { VELLUM_WORKFLOW_ROOT_MODULE_PATH } from "src/constants";
import { BasePersistedFile } from "src/generators/base-persisted-file";
import { NodeNotFoundError } from "src/generators/errors";
import { AstNode } from "src/generators/extensions/ast-node";
import { BoolInstantiation } from "src/generators/extensions/bool-instantiation";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { CodeBlock } from "src/generators/extensions/code-block";
import { Field } from "src/generators/extensions/field";
import { ListInstantiation } from "src/generators/extensions/list-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { Json } from "src/generators/json";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  ConstantValueWorkflowReference,
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
    const datasetField = new Field({
      name: "dataset",
      initializer: new ListInstantiation(
        this.sandboxInputs.map((input, index) =>
          this.getWorkflowInput(input, index)
        ),
        { endWithComma: true }
      ),
    });
    this.inheritReferences(datasetField);

    const sandboxRunnerField = new Field({
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
      new CodeBlock(`\
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
    const triggerAttributeKeys = new Set(
      trigger?.attributes.map((attr) => attr.key) ?? []
    );

    // Separate inputs into trigger attribute inputs and workflow inputs
    const workflowInputs = hasInputs
      ? inputs.filter(
          (input) =>
            !triggerAttributeKeys.has(removeEscapeCharacters(input.name))
        )
      : [];

    // Add workflow inputs (excluding trigger attribute inputs)
    if (workflowInputs.length > 0) {
      const inputsInstance = new ClassInstantiation({
        classReference: new Reference({
          name: "Inputs",
          modulePath: getGeneratedInputsModulePath(this.workflowContext),
        }),
        arguments_: workflowInputs
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

    if (!isNil(workflowTriggerId)) {
      const triggerInstance = this.getTriggerInstance(
        workflowTriggerId,
        inputs
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

  private isConstantTrueCondition(
    whenCondition: WorkflowSandboxDatasetRowMock["when_condition"]
  ): boolean {
    if (isNil(whenCondition)) {
      return false;
    }

    const constantValueCondition =
      whenCondition as ConstantValueWorkflowReference;
    if (constantValueCondition.type !== "CONSTANT_VALUE") {
      return false;
    }

    return constantValueCondition.value?.value === true;
  }

  private getMockNodeExecution(
    mock: WorkflowSandboxDatasetRowMock
  ): ClassInstantiation | null {
    // Skip generating MockNodeExecution if then_outputs is undefined
    if (isNil(mock.then_outputs)) {
      return null;
    }

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

    // If when_condition is a constant true value, return the Node's Outputs directly
    if (this.isConstantTrueCondition(mock.when_condition)) {
      return thenOutputsInstance;
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

    arguments_.push(
      new MethodArgument({
        name: "then_outputs",
        value: thenOutputsInstance,
      })
    );

    // Generate disabled parameter if it's true
    if (mock.disabled === true) {
      arguments_.push(
        new MethodArgument({
          name: "disabled",
          value: new BoolInstantiation(true),
        })
      );
    }

    return new ClassInstantiation({
      classReference: new Reference({
        name: "MockNodeExecution",
        modulePath: VELLUM_WORKFLOW_ROOT_MODULE_PATH,
      }),
      arguments_,
    });
  }

  private getTriggerInstance(
    workflowTriggerId: string,
    inputs?: WorkflowSandboxInputs
  ): ClassInstantiation | undefined {
    const triggers = this.workflowContext.triggers ?? [];
    const trigger = triggers.find((t) => t.id === workflowTriggerId);

    if (!trigger) {
      return undefined;
    }

    const triggerClassInfo = getTriggerClassInfo(trigger, this.workflowContext);

    // Generate arguments for the trigger instance based on its attributes,
    // using provided dataset inputs when available, else default to None.
    const arguments_: MethodArgument[] = trigger.attributes.map((attr) => {
      const matchingInput =
        inputs?.find(
          (i) => removeEscapeCharacters(i.name) === attr.key && !isNil(i.value)
        ) ?? null;

      return new MethodArgument({
        name: attr.key,
        value: matchingInput
          ? vellumValue({ vellumValue: matchingInput })
          : new NoneInstantiation(),
      });
    });

    return new ClassInstantiation({
      classReference: new Reference({
        name: triggerClassInfo.className,
        modulePath: triggerClassInfo.modulePath,
      }),
      arguments_,
    });
  }
}
