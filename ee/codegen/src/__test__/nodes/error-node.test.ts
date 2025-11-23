import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { errorNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { ErrorNodeContext } from "src/context/node-context/error-node";
import { Writer } from "src/generators/extensions/writer";
import { ErrorNode } from "src/generators/nodes/error-node";

describe("ErrorNode", () => {
  let workflowContext: WorkflowContext;
  let node: ErrorNode;
  let writer: Writer;

  beforeEach(async () => {
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory();
      writer = new Writer();

      const nodeData = errorNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ErrorNodeContext;

      node = new ErrorNode({
        workflowContext,
        nodeContext,
      });
    });

    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it(`getNodeDisplayFile`, async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("should codegen successfully without error source inputs", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });

      const nodeData = errorNodeDataFactory({
        errorSourceInputs: [],
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as ErrorNodeContext;

      node = new ErrorNode({
        workflowContext,
        nodeContext,
      });
    });

    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it(`getNodeDisplayFile`, async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
