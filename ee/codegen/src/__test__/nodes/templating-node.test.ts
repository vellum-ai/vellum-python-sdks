import { Writer } from "@fern-api/python-ast/core/Writer";
import { VellumVariableType } from "vellum-ai/api/types";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { templatingNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";

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
    beforeEach(async () => {
      const nodeData = templatingNodeFactory({
        errorOutputId: "e7a1fbea-f5a7-4b31-a9ff-0d26c3de021f",
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
});
