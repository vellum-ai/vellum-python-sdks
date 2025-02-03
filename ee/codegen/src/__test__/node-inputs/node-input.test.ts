import { Writer } from "@fern-api/python-ast/core/Writer";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeInput as NodeInputType, WorkflowDataNode } from "src/types/vellum";

describe("NodeInput", () => {
  let writer: Writer;
  let workflowContext: WorkflowContext;
  let nodeContext: BaseNodeContext<WorkflowDataNode>;

  beforeEach(async () => {
    writer = new Writer();
    workflowContext = workflowContextFactory();
    nodeContext = await nodeContextFactory({ workflowContext });
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
      workflowContext,
      nodeInputData,
    });

    nodeInput.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
