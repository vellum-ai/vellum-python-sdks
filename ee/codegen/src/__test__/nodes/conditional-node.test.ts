import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuid4 } from "uuid";
import { beforeEach, describe, it, expect } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  conditionalNodeWithNullOperatorFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ConditionalNodeContext } from "src/context/node-context/conditional-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
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
});

describe("ConditionalNode with invalid uuid for field and value node input ids", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const nodeData = constructConditionalNodeWithInvalidUUID();

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

  function constructConditionalNodeWithInvalidUUID(): ConditionalNodeType {
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
                  fieldNodeInputId:
                    "2cb6582e-c329-4952-8598-097830b766c7|cf63d0ad-5e52-4031-a29f-922e7004cdd8",
                  operator: "=",
                  valueNodeInputId:
                    "b51eb7cd-3e0a-4b42-a269-d58ebc3e0b04|51315413-f47c-4d7e-bc94-bd9e7862043d",
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
          id: "2cb6582e-c329-4952-8598-097830b766c7|cf63d0ad-5e52-4031-a29f-922e7004cdd8",
          key: "2cb6582e-c329-4952-8598-097830b766c7|cf63d0ad-5e52-4031-a29f-922e7004cdd8",
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
        {
          id: "b51eb7cd-3e0a-4b42-a269-d58ebc3e0b04|51315413-f47c-4d7e-bc94-bd9e7862043d",
          key: "b51eb7cd-3e0a-4b42-a269-d58ebc3e0b04|51315413-f47c-4d7e-bc94-bd9e7862043d",
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

describe("ConditionalNode with null operator", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const templatingNode = templatingNodeFactory();
    const nodeData = conditionalNodeWithNullOperatorFactory({
      nodeOutputReference: {
        nodeId: templatingNode.id,
        outputId: templatingNode.data.outputId,
      },
    });

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

    (await createNodeContext({
      workflowContext,
      nodeData: templatingNode,
    })) as TemplatingNodeContext;

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;

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
          "Node Conditional Node is missing required left-hand side input field for rule: 0 in condition: 0"
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

describe("Conditional Node with numeric operator casts rhs to NUMBER", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "d2287fee-98fb-421c-9464-e54d8f70f046",
          key: "rhs",
          type: "NUMBER",
        },
        workflowContext,
      })
    );

    const nodeData: ConditionalNodeType = {
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
                  operator: ">",
                  valueNodeInputId: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
                },
              ],
              combinator: "AND",
            },
          },
        ],
        version: "2",
      },
      inputs: [
        {
          id: "2cb6582e-c329-4952-8598-097830b766c7",
          key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.field",
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
        {
          id: "cf63d0ad-5e52-4031-a29f-922e7004cdd8",
          key: "ad6bcb67-f21b-4af9-8d4b-ac8d3ba297cc.value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "0.5",
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

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("getNodeFile", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});

describe("Conditional Node warning cases", () => {
  let writer: Writer;

  beforeEach(async () => {
    writer = new Writer();
  });

  it("getNodeFile should be resilient to lhs referencing a non-existent node", async () => {
    const workflowContext = workflowContextFactory({ strict: false });

    const referenceNodeId = uuid4();
    const nodeData = conditionalNodeFactory({
      // Non-existent node output reference
      inputReferenceId: uuid4(),
      inputReferenceNodeId: referenceNodeId,
    });

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;

    const node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });

    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();

    // Ideally, we reduce the number of warnings to 1 in the future
    const errors = workflowContext.getErrors();
    expect(errors.length).toBe(2);
    expect(errors[0]?.message).toBe(
      `Failed to find node with id '${referenceNodeId}'`
    );
    expect(errors[1]?.message).toBe(
      `Node Conditional Node is missing required left-hand side input field for rule: 0 in condition: 0`
    );
    expect(errors[0]?.severity).toBe("WARNING");
    expect(errors[1]?.severity).toBe("WARNING");
  });
  it("should log warning when lhs key is missing", async () => {
    const workflowContext = workflowContextFactory({ strict: false });

    const nodeData = conditionalNodeFactory();
    // Remove the input field key
    nodeData.inputs = [];

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;

    const node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });

    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();

    const errors = workflowContext.getErrors();
    expect(errors.length).toBe(1);
    expect(errors[0]?.message).toBe(
      "Node Conditional Node is missing required left-hand side input field for rule: 0 in condition: 0"
    );
    expect(errors[0]?.severity).toBe("WARNING");
  });
});
describe("ConditionalNode with empty rules array", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    // Creating a node where conditionData.rules is an empty array []
    const nodeData = conditionalNodeFactory({
      conditions: [
        {
          id: "empty-condition",
          type: "IF",
          sourceHandleId: "some-handle-id",
          data: {
            id: "empty-condition-data",
            rules: [], // EMPTY RULES ARRAY
            combinator: "AND",
          },
        },
      ],
    });

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

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("should not throw error due to empty reduce without initial value", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});

describe("Conditional Node with constant value string lhs", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const nodeData: ConditionalNodeType = {
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
                  id: "895d82e8-e6d4-4033-9ae4-581e8c2dc45c",
                  fieldNodeInputId: "f804da22-b3d2-43d0-8c6f-321434c28ead",
                  operator: "=",
                  valueNodeInputId: "c2e0ebfc-e079-4b7e-a926-f7ba671995dc",
                },
              ],
              combinator: "AND",
            },
          },
        ],
        version: "2",
      },
      inputs: [
        {
          id: "f804da22-b3d2-43d0-8c6f-321434c28ead",
          key: "895d82e8-e6d4-4033-9ae4-581e8c2dc45c.field",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "hello",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "c2e0ebfc-e079-4b7e-a926-f7ba671995dc",
          key: "895d82e8-e6d4-4033-9ae4-581e8c2dc45c.value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "world",
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

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("getNodeFile", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});

describe("Conditional Node with constant value string base", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: ConditionalNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    const nodeData: ConditionalNodeType = {
      id: "b81a4453-7b80-41ea-bd55-c62df8878fd3",
      type: WorkflowNodeType.CONDITIONAL,
      data: {
        label: "Conditional Node",
        targetHandleId: "842b9dda-7977-47ad-a322-eb15b4c7069d",
        conditions: [
          {
            id: "d93fecd6-0f6c-4c13-b572-2254404650cd",
            type: "IF",
            sourceHandleId: "b9a8c7af-68bf-42e0-9643-a62d73734c74",
            data: {
              id: "55f430c7-a98e-4c40-a2b3-455f7152556a",
              rules: [
                {
                  id: "895d82e8-e6d4-4033-9ae4-581e8c2dc45c",
                  fieldNodeInputId: "f804da22-b3d2-43d0-8c6f-321434c28ead",
                  operator: "between",
                  valueNodeInputId: "c2e0ebfc-e079-4b7e-a926-f7ba671995dc",
                },
              ],
              combinator: "AND",
            },
          },
        ],
        version: "2",
      },
      inputs: [
        {
          id: "f804da22-b3d2-43d0-8c6f-321434c28ead",
          key: "895d82e8-e6d4-4033-9ae4-581e8c2dc45c.field",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "hello",
                },
              },
            ],
            combinator: "OR",
          },
        },
        {
          id: "c2e0ebfc-e079-4b7e-a926-f7ba671995dc",
          key: "895d82e8-e6d4-4033-9ae4-581e8c2dc45c.value",
          value: {
            rules: [
              {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "world,hello",
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

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as ConditionalNodeContext;

    node = new ConditionalNode({
      workflowContext,
      nodeContext,
    });
  });

  it("getNodeFile", async () => {
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
