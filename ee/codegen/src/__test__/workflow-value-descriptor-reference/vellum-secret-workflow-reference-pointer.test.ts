import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { VellumSecretWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/vellum-secret-workflow-reference-pointer";
import { WorkflowValueDescriptorReference } from "src/types/vellum";

describe("VellumSecretWorkflowReferencePointer", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
  });

  it("should generate correct AST for vellum secret reference", async () => {
    const secretReference: WorkflowValueDescriptorReference = {
      type: "VELLUM_SECRET",
      vellumSecretName: "test-secret",
    };

    const pointer = new VellumSecretWorkflowReferencePointer({
      workflowContext,
      nodeInputWorkflowReferencePointer: secretReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
