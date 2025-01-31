import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { WorkflowContext } from "src/context";
import { WorkflowInputReferencePointer } from "src/generators/workflow-value-descriptor-reference/workflow-input-reference-pointer";
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

    const pointer = new WorkflowInputReferencePointer({
      workflowContext,
      nodeInputWorkflowReferencePointer: workflowInputReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
