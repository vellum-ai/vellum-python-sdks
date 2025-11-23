import { nodeContextFactory } from "src/__test__/helpers";
import * as codegen from "src/codegen";
import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
import { NodeInput as NodeInputType, WorkflowDataNode } from "src/types/vellum";

describe("NodeInput", () => {
  let writer: Writer;
  let nodeContext: BaseNodeContext<WorkflowDataNode>;

  beforeEach(async () => {
    writer = new Writer();
    nodeContext = await nodeContextFactory();
  });

  it("should generate correct Python code", async () => {
    const nodeInputData: NodeInputType = {
      id: "test-input-id",
      key: "test-input-key",
      value: {
        rules: [
          {
            type: "CONSTANT_VALUE",
            data: {
              type: "STRING",
              value: "test-value",
            },
          },
        ],
        combinator: "OR",
      },
    };

    const nodeInput = codegen.nodeInput({
      nodeContext,
      nodeInputData,
    });

    nodeInput.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
