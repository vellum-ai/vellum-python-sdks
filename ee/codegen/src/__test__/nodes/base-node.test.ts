import { workflowContextFactory } from "src/__test__/helpers";
import {
  genericNodeFactory,
  templatingNodeFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import {
  NodeAttributeGenerationError,
  NodeDefinitionGenerationError,
} from "src/generators/errors";
import { Writer } from "src/generators/extensions/writer";
import { GenericNode } from "src/generators/nodes/generic-node";
import { TemplatingNode } from "src/generators/nodes/templating-node";

describe("BaseNode", () => {
  describe("failures", () => {
    it("should throw the expected error when a input references an invalid node", async () => {
      const workflowContext = workflowContextFactory();

      const templatingNodeData = templatingNodeFactory({
        inputs: [
          {
            id: "9feb7b5e-5947-496d-b56f-1e2627730796",
            key: "text",
            value: {
              rules: [
                {
                  type: "NODE_OUTPUT",
                  data: {
                    nodeId: "12345678-1234-5678-1234-567812345678",
                    outputId: "90abcdef-90ab-cdef-90ab-cdef90abcdef",
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
      const templatingNodeContext = (await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData,
      })) as TemplatingNodeContext;

      expect(() => {
        new TemplatingNode({
          workflowContext,
          nodeContext: templatingNodeContext,
        });
      }).toThrow(
        new NodeAttributeGenerationError(
          "Failed to generate attribute 'TemplatingNode.inputs.text': Failed to find node with id '12345678-1234-5678-1234-567812345678'",
          "WARNING"
        )
      );
    });

    it("should throw the expected error when a input references an invalid output", async () => {
      const workflowContext = workflowContextFactory();

      const templatingNodeData = templatingNodeFactory().build();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData,
      });

      const templatingNode2Data = templatingNodeFactory({
        label: "TemplatingNode2",
        id: "12345678-1234-5678-1234-567812345678",
        sourceHandleId: "12345678-1234-5678-1234-567812345679",
        targetHandleId: "12345678-1234-5678-1234-56781234567a",
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
                    outputId: "90abcdef-90ab-cdef-90ab-cdef90abcdef",
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
      const templatingNode2Context = (await createNodeContext({
        workflowContext,
        nodeData: templatingNode2Data,
      })) as TemplatingNodeContext;

      expect(() => {
        new TemplatingNode({
          workflowContext,
          nodeContext: templatingNode2Context,
        });
      }).toThrow(
        new NodeAttributeGenerationError(
          "Failed to generate attribute 'TemplatingNode2.inputs.text': Failed to find TemplatingNode Output with id '90abcdef-90ab-cdef-90ab-cdef90abcdef'",
          "WARNING"
        )
      );
    });

    it(`should generate base nodes as much as possible for non strict workflow contexts`, async () => {
      vi.spyOn(
        GenericNode.prototype,
        "getNodeClassBodyStatements"
      ).mockImplementation(() => {
        throw new NodeDefinitionGenerationError("test");
      });

      const workflowContext = workflowContextFactory({
        strict: false,
      });
      const writer = new Writer();

      const nodeData = genericNodeFactory();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      const node = new GenericNode({
        workflowContext,
        nodeContext,
      });

      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
