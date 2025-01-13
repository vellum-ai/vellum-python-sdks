import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { mergeNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { MergeNodeContext } from "src/context/node-context/merge-node";
import { MergeNode } from "src/generators/nodes/merge-node";

describe("MergeNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: MergeNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = mergeNodeDataFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as MergeNodeContext;
      workflowContext.addNodeContext(nodeContext);

      node = new MergeNode({
        workflowContext: workflowContext,
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
