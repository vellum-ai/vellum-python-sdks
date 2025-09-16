import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
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

  it("should generate display data with icon and color when provided in serialized JSON", async () => {
    const nodeData = createGenericNodeWithDisplayData({
      position: { x: 100, y: 200 },
      icon: "vellum:icon:star",
      color: "navy",
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

    expect(result).toContain('icon="vellum:icon:star"');
    expect(result).toContain('color="navy"');
  });

  it("should not include icon and color when not provided in serialized JSON", async () => {
    const nodeData = createGenericNodeWithDisplayData({
      position: { x: 50, y: 75 },
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

    expect(result).not.toContain("icon=");
    expect(result).not.toContain("color=");
  });
});
