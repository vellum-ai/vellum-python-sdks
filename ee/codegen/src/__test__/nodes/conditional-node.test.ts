import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  conditionalNodeWithNullOperatorFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { ConditionalNode } from "src/generators/nodes/conditional-node";
import {
  ConditionalNode as ConditionalNodeType,
  WorkflowNodeType,
} from "src/types/vellum";

describe("ConditionalNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const nodeData = conditionalNodeFactory({ includeElif: true });

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "d2287fee-98fb-421c-9464-e54d8f70f046",
          key: "field",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;
    workflowContext.addNodeContext(nodeContext);

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("getNodeFile", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("getNodeDisplayFile", async () => {
    node.getNodeDisplayFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("getNodeDefinition", () => {
    expect(node.nodeContext.getNodeDefinition()).toMatchSnapshot();
  });
});

describe("ConditionalNode with null operator", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const nodeData = conditionalNodeWithNullOperatorFactory();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "d2287fee-98fb-421c-9464-e54d8f70f046",
          key: "field",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;
    workflowContext.addNodeContext(nodeContext);

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("getNodeFile", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("getNodeDisplayFile", async () => {
    node.getNodeDisplayFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("getNodeDefinition", () => {
    expect(node.nodeContext.getNodeDefinition()).toMatchSnapshot();
  });
});

describe("ConditionalNode with incorrect rule id references", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const invalidNodeData = constructInvalidConditionalNode();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "d2287fee-98fb-421c-9464-e54d8f70f046",
          key: "field",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData: invalidNodeData,
    })) as ConditionalNodeContext;
    workflowContext.addNodeContext(nodeContext);

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("getNodeFile should throw error", async () => {
    try {
      node.getNodeFile().write(writer);
      await writer.toStringFormatted();
    } catch (error: unknown) {
      if (error instanceof Error) {
        expect(error.message).toBe(
          "Could not find input field key given ruleId: ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc on rule index: 0 on condition index: 0 for node: Conditional Node"
        );
      } else {
        throw new Error("Unexpected error type");
      }
    }
  });

  function constructInvalidConditionalNode(): ConditionalNodeType {
    return {
      id: "b81a4453-7b80-41ea-bd55-c62df8878fd3",
      type: WorkflowNodeType.CONDITIONAL,
      data: {
        label: "Conditional Node",
        targetHandleId: "842b9dda-7977-47ad-a322-eb15b4c7069d",
        conditions: [
          {
            id: "8d0d8b56-6c17-4684-9f16-45dd6ce23060",
            type: "IF",
            sourceHandleId: "63345ab5-1a4d-48a1-ad33-91bec41f92a5",
            data: {
              id: "fa50fb0c-8d62-40e3-bd88-080b52efd4b2",
              rules: [
                {
                  id: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc",
                  rules: [],
                  fieldNodeInputId: "2cb6582e-c329-4952-8598-097830b766c7",
                  operator: "=",
                  valueNodeInputId: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
                },
              ],
              combinator: "AND",
            },
          },
          {
            id: "ea63ccd5-3fe3-4371-ba3c-6d3ec7ca2b60",
            type: "ELSE",
            sourceHandleId: "14a8b603-6039-4491-92d4-868a4dae4c15",
          },
        ],
        version: "2",
      },
      inputs: [
        {
          id: "non-existent-id",
          key: "non-existent-rule-id.field",
          value: {
            rules: [
              {
                type: "INPUT_VARIABLE",
                data: {
                  inputVariableId: "d2287fee-98fb-421c-9464-e54d8f70f046",
                },
              },
            ],
            combinator: "OR",
          },
        },
      ],
      displayData: {
        width: 480,
        height: 180,
        position: {
          x: 2247.2797390213086,
          y: 30.917121251477084,
        },
      },
    };
  }
});
