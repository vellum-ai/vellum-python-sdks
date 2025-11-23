import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";
import { WorkflowInputReference } from "src/generators/workflow-value-descriptor-reference/workflow-input-reference";
import { WorkflowValueDescriptorReference } from "src/types/vellum";

describe("WorkflowInputReferencePointer", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "someVariableId",
          key: "testVariable",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  it("should generate correct AST for workflow input reference", async () => {
    const workflowInputReference: WorkflowValueDescriptorReference = {
      type: "WORKFLOW_INPUT",
      inputVariableId: "someVariableId",
    };

    const pointer = new WorkflowInputReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: workflowInputReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
