import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";
import { VellumVariableType } from "vellum-ai/api/types";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { templatingNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";
import { TemplatingNode as TemplatingNodeType } from "src/types/vellum";

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
      const nodeData = templatingNodeFactory();

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
      });

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
      });

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
      });

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
});
