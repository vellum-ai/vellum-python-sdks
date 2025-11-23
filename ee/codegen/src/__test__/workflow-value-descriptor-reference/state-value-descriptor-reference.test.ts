import { workflowContextFactory } from "src/__test__/helpers";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";
import { WorkflowStateReference } from "src/generators/workflow-value-descriptor-reference/workflow-state-reference";
import { WorkflowValueDescriptorReference } from "src/types/vellum";

describe("StateValueDescriptorReference", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    workflowContext.addStateVariableContext(
      stateVariableContextFactory({
        stateVariableData: {
          id: "someVariableId",
          key: "testVariable",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  it("should generate correct AST for workflow input reference", async () => {
    const stateVariableReference: WorkflowValueDescriptorReference = {
      type: "WORKFLOW_STATE",
      stateVariableId: "someVariableId",
    };

    const pointer = new WorkflowStateReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: stateVariableReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
