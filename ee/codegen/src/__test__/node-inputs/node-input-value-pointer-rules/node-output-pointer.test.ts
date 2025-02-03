import { Writer } from "@fern-api/python-ast/core/Writer";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeOutputPointerRule } from "src/generators/node-inputs";
import { WorkflowDataNode } from "src/types/vellum";

describe("NodeOutputPointer", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct Python code", async () => {
    const workflowContext = workflowContextFactory();
    vi.spyOn(workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeContext = await nodeContextFactory({ workflowContext });

    const nodeOutputPointer = new NodeOutputPointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "NODE_OUTPUT",
        data: {
          nodeId: "test-node-id",
          outputId: "test-output-id",
        },
      },
    });

    nodeOutputPointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
