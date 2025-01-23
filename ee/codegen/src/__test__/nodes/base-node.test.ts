import { workflowContextFactory } from "src/__test__/helpers";
import { templatingNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext } from "src/context";
import { TemplatingNodeContext } from "src/context/node-context/templating-node";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { TemplatingNode } from "src/generators/nodes/templating-node";

describe("BaseNode", () => {
  describe("failures", () => {
    it("should throw the expected error when a input references an invalid node", async () => {
      const workflowContext = workflowContextFactory();

      const templatingNodeData = templatingNodeFactory({
        inputRules: [
          {
            type: "NODE_OUTPUT",
            data: {
              nodeId: "12345678-1234-5678-1234-567812345678",
              outputId: "90abcdef-90ab-cdef-90ab-cdef90abcdef",
            },
          },
        ],
      });
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
          "Failed to generate attribute 'TemplatingNode.inputs.text': Failed to find node with id '12345678-1234-5678-1234-567812345678'"
        )
      );
    });

    it("should throw the expected error when a input references an invalid output", async () => {
      const workflowContext = workflowContextFactory();

      const templatingNodeData = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData,
      });

      const templatingNode2Data = templatingNodeFactory({
        label: "TemplatingNode2",
        id: "12345678-1234-5678-1234-567812345678",
        sourceHandleId: "12345678-1234-5678-1234-567812345679",
        targetHandleId: "12345678-1234-5678-1234-56781234567a",
        inputRules: [
          {
            type: "NODE_OUTPUT",
            data: {
              nodeId: templatingNodeData.id,
              outputId: "90abcdef-90ab-cdef-90ab-cdef90abcdef",
            },
          },
        ],
      });
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
          "Failed to generate attribute 'TemplatingNode2.inputs.text': Failed to find output with id '90abcdef-90ab-cdef-90ab-cdef90abcdef'"
        )
      );
    });
  });
});
