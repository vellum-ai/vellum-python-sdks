import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  genericNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { GenericNode } from "src/generators/nodes/generic-node";
import { NodeAttribute } from "src/types/vellum";

describe("GenericNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: GenericNode;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

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
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = genericNodeFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      workflowContext.addNodeContext(nodeContext);

      node = new GenericNode({
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

  describe("basic with node output as attribute", () => {
    beforeEach(async () => {
      const referencedNode = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
      });

      const referencedNodeContext = (await createNodeContext({
        workflowContext,
        nodeData: referencedNode,
      })) as InlinePromptNodeContext;
      workflowContext.addNodeContext(referencedNodeContext);

      const nodeAttributes: NodeAttribute[] = [
        {
          id: "attr-1",
          name: "default-attribute",
          value: {
            type: "NODE_OUTPUT",
            data: {
              nodeId: referencedNode.id,
              outputId: referencedNode.data.outputId,
            },
          },
        },
      ];

      const nodeData = genericNodeFactory({
        name: "MyCustomNode",
        nodeAttributes: nodeAttributes,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      workflowContext.addNodeContext(nodeContext);

      node = new GenericNode({
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
