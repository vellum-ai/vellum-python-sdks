import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
import { NodeOutputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/node-output-workflow-reference";
import {
  WorkflowDataNode,
  WorkflowValueDescriptorReference,
} from "src/types/vellum";

describe("NodeOutputWorkflowReferencePointer", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    vi.spyOn(workflowContext, "findNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);
  });

  it("should generate correct AST for node output reference", async () => {
    const nodeOutputReference: WorkflowValueDescriptorReference = {
      type: "NODE_OUTPUT",
      nodeId: "test-node",
      nodeOutputId: "test-output",
    };

    const pointer = new NodeOutputWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: nodeOutputReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
