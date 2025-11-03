import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { GenericNode } from "src/generators/nodes/generic-node";

describe("NodeDisplay", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-1",
          key: "input_1",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  it.each([
    {
      name: "with icon and color",
      displayData: { icon: "🎨", color: "#FF5733" },
    },
    {
      name: "with only icon",
      displayData: { icon: "🔧" },
    },
    {
      name: "with only color",
      displayData: { color: "#00FF00" },
    },
    {
      name: "without icon or color",
      displayData: { position: { x: 100, y: 200 } },
    },
    {
      name: "with null icon and color",
      displayData: { icon: null, color: null },
    },
  ])("$name", async ({ displayData }) => {
    const nodeData = genericNodeFactory({ label: "MyCustomNode" });
    nodeData.displayData = displayData;

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as GenericNodeContext;

    const node = new GenericNode({ workflowContext, nodeContext });
    const nodeClass = node.generateNodeClass();

    const writer = new Writer();
    nodeClass.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
