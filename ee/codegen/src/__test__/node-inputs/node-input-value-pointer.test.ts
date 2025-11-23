import { describe, it, expect, beforeEach } from "vitest";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { WorkflowContext, createNodeContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
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
    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node1",
        label: "TestNode",
        nodeOutputs: [
          {
            id: "output1",
            name: "my_output",
            type: "STRING",
          },
        ],
      }),
    });

    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node2",
        label: "TestNode",
        nodeOutputs: [
          {
            id: "output2",
            name: "my_output",
            type: "STRING",
          },
        ],
      }),
    });

    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node3",
        label: "TestNode",
        nodeOutputs: [
          {
            id: "output3",
            name: "my_output",
            type: "STRING",
          },
        ],
      }),
    });

    const nodeContext = await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory(),
    });

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
    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node1",
        label: "TestNode",
        nodeOutputs: [
          {
            id: "output1",
            name: "my_output",
            type: "STRING",
          },
        ],
      }),
    });

    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node2",
        label: "TestNode",
        nodeOutputs: [
          {
            id: "output2",
            name: "my_output",
            type: "STRING",
          },
        ],
      }),
    });

    const nodeContext = await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory(),
    });

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
    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node1",
        label: "TestNode",
        nodeOutputs: [
          {
            id: "output1",
            name: "my_output",
            type: "STRING",
          },
        ],
      }),
    });

    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node2",
        label: "TestNode2",
        nodeOutputs: [
          {
            id: "output2",
            name: "output2",
            type: "STRING",
          },
        ],
      }),
    });
    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node3",
        label: "TestNode3",
        nodeOutputs: [
          {
            id: "output3",
            name: "output3",
            type: "STRING",
          },
        ],
      }),
    });
    const nodeContext = await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory(),
    });

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
