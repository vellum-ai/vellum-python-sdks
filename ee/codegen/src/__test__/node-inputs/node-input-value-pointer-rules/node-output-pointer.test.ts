import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { Writer } from "src/generators/extensions/writer";
import { NodeOutputPointerRule } from "src/generators/node-inputs";

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
    const nodeData = genericNodeFactory({
      id: "test-node-id",
      label: "TestNode",
      nodeOutputs: [
        { id: "test-output-id", name: "my-output", type: "STRING" },
      ],
    });
    await nodeContextFactory({ workflowContext, nodeData });
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
