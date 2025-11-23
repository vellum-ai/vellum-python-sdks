import { v4 as uuidv4 } from "uuid";
import { VellumVariableType } from "vellum-ai/api/types";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  nodePortFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { NodeNotFoundError } from "src/generators/errors";
import { Writer } from "src/generators/extensions/writer";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import {
  NodePort,
  TemplatingNode as TemplatingNodeType,
} from "src/types/vellum";

describe("TemplatingNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: TemplatingNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "90c6afd3-06cc-430d-aed1-35937c062531",
          key: "text",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = templatingNodeFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
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

  describe("basic with json output type", () => {
    beforeEach(async () => {
      const nodeData = templatingNodeFactory({
        outputType: VellumVariableType.Json,
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
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

  describe("reject on error enabled", () => {
    let templatingNodeData: TemplatingNodeType;
    const errorOutputId = "e7a1fbea-f5a7-4b31-a9ff-0d26c3de021f";

    beforeEach(async () => {
      templatingNodeData = templatingNodeFactory({
        errorOutputId,
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
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

    it("should generate the node file for a dependency correctly", async () => {
      const nextTemplatingNode = templatingNodeFactory({
        id: uuidv4(),
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
        inputs: [
          {
            id: "9feb7b5e-5947-496d-b56f-1e2627730796",
            key: "text",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    nodeId: templatingNodeData.id,
                    outputId: errorOutputId,
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "7b8af68b-cf60-4fca-9c57-868042b5b616",
            key: "template",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "Hello, World!",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
      }).build();

      const nextTemplatingNodeContext = (await createNodeContext({
        workflowContext,
        nodeData: nextTemplatingNode,
      })) as TemplatingNodeContext;

      const nextTemplatingNodeAst = new TemplatingNode({
        workflowContext,
        nodeContext: nextTemplatingNodeContext,
      });

      nextTemplatingNodeAst.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("referencing an invalid node", () => {
    it("getNodeFile", async () => {
      const workflowContext = workflowContextFactory({ strict: false });
      const templateNodeInputId = uuidv4();
      const nodeData = templatingNodeFactory({
        templateNodeInputId,
        inputs: [
          {
            id: uuidv4(),
            key: "text",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    nodeId: uuidv4(), // invalid node id
                    outputId: uuidv4(),
                  },
                },
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "JSON",
                    value: {},
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: templateNodeInputId,
            key: "template",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "Hello, World!",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      const node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeFile().write(writer);

      expect(workflowContext.getErrors()).toHaveLength(1);
      expect(workflowContext.getErrors()[0]).toBeInstanceOf(NodeNotFoundError);
      expect(workflowContext.getErrors()[0]?.message).toContain(
        "Failed to find node with id "
      );
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with node ports", () => {
    beforeEach(async () => {
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
      const sourceHandleId = "308675dd-2e68-45a5-86fa-b2647a92f553";
      const nodePortsData: NodePort[] = [
        nodePortFactory({
          type: "IF",
          id: sourceHandleId,
        }),
        nodePortFactory({
          type: "ELSE",
          id: "1db0ebfd-c07e-49ed-9c4e-4822d3010367",
        }),
      ];

      const nodeData = templatingNodeFactory({
        sourceHandleId: sourceHandleId,
      })
        .withPorts(nodePortsData)
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("with environment variable", () => {
    beforeEach(async () => {
      const nodeData = templatingNodeFactory({
        inputs: [
          {
            id: "de3807c0-eaaa-4fa9-9997-309c243b9654",
            key: "my_test_environment_variable",
            value: {
              rules: [
                {
                  type: "ENVIRONMENT_VARIABLE",
                  data: {
                    environmentVariable: "MY_TEST_ENVIRONMENT_VARIABLE",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TemplatingNodeContext;

      node = new TemplatingNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
