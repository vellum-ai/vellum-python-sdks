import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";
import { EnvironmentVariableWorkflowReference } from "src/generators/workflow-value-descriptor-reference/environment-variable-workflow-reference";
import { WorkflowValueDescriptorReference } from "src/types/vellum";

describe("EnvironmentVariableWorkflowReference", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
  });

  it("should generate correct AST for environment variable reference", async () => {
    const envVarReference: WorkflowValueDescriptorReference = {
      type: "ENVIRONMENT_VARIABLE",
      environmentVariable: "API_KEY",
    };

    const pointer = new EnvironmentVariableWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: envVarReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
