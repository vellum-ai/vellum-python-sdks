import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { Writer } from "src/generators/extensions/writer";
import { GenericNode } from "src/generators/nodes/generic-node";
import {
  GenericNode as GenericNodeType,
  GenericNodeDisplayData,
} from "src/types/vellum";

describe("GenericNode DisplayData Integration", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory({ strict: false });
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-1",
          key: "count",
          type: "NUMBER",
        },
        workflowContext,
      })
    );
  });

  // Helper function to create a minimal generic node with display data
  const createGenericNodeWithDisplayData = (
    displayData: GenericNodeDisplayData | undefined
  ): GenericNodeType => ({
    id: "test-node-id",
    label: "TestDisplayNode",
    type: "GENERIC",
    displayData,
    base: {
      module: ["vellum", "workflows", "nodes", "bases", "base"],
      name: "BaseNode",
    },
    trigger: { id: "trigger-1", mergeBehavior: "AWAIT_ALL" },
    ports: [{ id: "port-1", name: "default", type: "DEFAULT" }],
    attributes: [],
    outputs: [],
  });

  it("should not include icon and color in display data even when provided in serialized JSON", async () => {
    /**
     * Tests that icon and color are not generated in NodeDisplayData since they're now generated in BaseNode.Display.
     */
    // GIVEN a generic node with icon and color in display data
    const nodeData = createGenericNodeWithDisplayData({
      position: { x: 100, y: 200 },
      icon: "vellum:icon:star",
      color: "navy",
    });

    // WHEN we generate the node display file
    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as GenericNodeContext;

    const node = new GenericNode({
      workflowContext,
      nodeContext,
    });

    node.getNodeDisplayFile().write(writer);
    const result = await writer.toStringFormatted();

    // THEN icon and color should not be included in the display data
    expect(result).not.toContain("icon=");
    expect(result).not.toContain("color=");
  });

  it("should generate display data with z_index when provided in serialized JSON", async () => {
    const nodeData = createGenericNodeWithDisplayData({
      position: { x: 25, y: 50 },
      z_index: 10,
    });

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as GenericNodeContext;

    const node = new GenericNode({
      workflowContext,
      nodeContext,
    });

    node.getNodeDisplayFile().write(writer);
    const result = await writer.toStringFormatted();

    expect(result).toContain("z_index=10");
  });

  it("should not generate display_data field when no display data is provided", async () => {
    const nodeData = createGenericNodeWithDisplayData(undefined);

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as GenericNodeContext;

    const node = new GenericNode({
      workflowContext,
      nodeContext,
    });

    node.getNodeDisplayFile().write(writer);
    const result = await writer.toStringFormatted();

    // Should not contain any display_data field at all
    expect(result).not.toContain("display_data=");
  });
});
