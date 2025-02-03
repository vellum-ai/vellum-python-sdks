import { Writer } from "@fern-api/python-ast/core/Writer";
import { describe, it, expect, beforeEach } from "vitest";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { NodeInputValuePointer } from "src/generators/node-inputs/node-input-value-pointer";
import {
  NodeInputValuePointer as NodeInputValuePointerType,
  WorkflowDataNode,
} from "src/types/vellum";

describe("NodeInputValuePointer", () => {
  let writer: Writer;
  let workflowContext: WorkflowContext;
  let nodeContext: BaseNodeContext<WorkflowDataNode>;

  beforeEach(async () => {
    writer = new Writer();
    workflowContext = workflowContextFactory();
    nodeContext = await nodeContextFactory({ workflowContext });
  });

  it("should handle a single constant value rule", async () => {
    const nodeInputValuePointerData: NodeInputValuePointerType = {
      combinator: "OR",
      rules: [
        {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "test_value",
          },
        },
      ],
    };

    const nodeInputValuePointer = new NodeInputValuePointer({
      nodeContext,
      nodeInputValuePointerData,
    });

    nodeInputValuePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle three node output pointer rules", async () => {
    vi.spyOn(nodeContext.workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeInputValuePointerData: NodeInputValuePointerType = {
      combinator: "OR",
      rules: [
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node1",
            outputId: "output1",
          },
        },
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node2",
            outputId: "output2",
          },
        },
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node3",
            outputId: "output3",
          },
        },
      ],
    };

    const nodeInputValuePointer = new NodeInputValuePointer({
      nodeContext,
      nodeInputValuePointerData,
    });

    nodeInputValuePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle two node output pointers and one constant value", async () => {
    vi.spyOn(nodeContext.workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeInputValuePointerData: NodeInputValuePointerType = {
      combinator: "OR",
      rules: [
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node1",
            outputId: "output1",
          },
        },
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node2",
            outputId: "output2",
          },
        },
        {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "constant_value",
          },
        },
      ],
    };

    const nodeInputValuePointer = new NodeInputValuePointer({
      nodeContext,
      nodeInputValuePointerData,
    });

    nodeInputValuePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle two node output pointers with a constant value in between", async () => {
    vi.spyOn(nodeContext.workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeInputValuePointerData: NodeInputValuePointerType = {
      combinator: "OR",
      rules: [
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node1",
            outputId: "output1",
          },
        },
        {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "constant_value",
          },
        },
        {
          type: "NODE_OUTPUT",
          data: {
            nodeId: "node3",
            outputId: "output3",
          },
        },
      ],
    };

    const nodeInputValuePointer = new NodeInputValuePointer({
      nodeContext,
      nodeInputValuePointerData,
    });

    nodeInputValuePointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
