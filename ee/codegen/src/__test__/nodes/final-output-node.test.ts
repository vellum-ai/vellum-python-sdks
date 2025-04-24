import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { finalOutputNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { FinalOutputNodeContext } from "src/context/node-context/final-output-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { Writer } from "src/generators/extensions";
import { FinalOutputNode } from "src/generators/nodes/final-output-node";

describe("FinalOutputNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: FinalOutputNode;

  beforeEach(() => {
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory();
      const nodeData = finalOutputNodeFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as FinalOutputNodeContext;

      node = new FinalOutputNode({
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

  describe("should codegen successfully without node input", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });
      const nodeData = finalOutputNodeFactory({ includeInput: false });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as FinalOutputNodeContext;

      node = new FinalOutputNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(workflowContext.getErrors()).toEqual([
        new NodeAttributeGenerationError(
          'No input found named "node_input"',
          "WARNING"
        ),
      ]);
      expect(workflowContext.getErrors()[0]?.severity).toEqual("WARNING");
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
