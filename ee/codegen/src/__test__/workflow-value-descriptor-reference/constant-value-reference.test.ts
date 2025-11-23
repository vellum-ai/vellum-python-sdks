import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";
import { ConstantValueReference } from "src/generators/workflow-value-descriptor-reference/constant-value-reference";
import { WorkflowValueDescriptorReference } from "src/types/vellum";

describe("ConstantValueReferencePointer", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
  });

  it("should generate correct AST for string constant value reference", async () => {
    const constantValueReference: WorkflowValueDescriptorReference = {
      type: "CONSTANT_VALUE",
      value: {
        type: "STRING",
        value: "test-value",
      },
    };

    const pointer = new ConstantValueReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: constantValueReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
