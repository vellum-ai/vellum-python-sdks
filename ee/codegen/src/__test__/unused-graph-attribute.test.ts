import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  entrypointNodeDataFactory,
  genericNodeFactory,
  conditionalNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
} from "./helpers/node-data-factories";

import * as codegen from "src/codegen";
import { createNodeContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";

describe("Workflow", () => {
  const entrypointNode = entrypointNodeDataFactory();
  describe("unused_graphs", () => {
    const runUnusedGraphsWorkflowTest = async (
      edgeFactoryNodePairs: EdgeFactoryNodePair[]
    ) => {
      const writer = new Writer();

      const nodes = Array.from(
        new Set(
          edgeFactoryNodePairs.flatMap(([source, target]) => [
            Array.isArray(source) ? source[0] : source,
            Array.isArray(target) ? target[0] : target,
          ])
        )
      );

      const edges = edgesFactory(edgeFactoryNodePairs);
      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes,
          edges,
        },
      });

      await Promise.all(
        nodes.map((node) => {
          if (node.type === "ENTRYPOINT") {
            return;
          }

          createNodeContext({
            workflowContext,
            nodeData: node,
          });
        })
      );

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    };

    it("should be empty when all nodes are connected to entrypoint", async () => {
      const connectedNode1 = genericNodeFactory({
        label: "ConnectedNode1",
      });
      const connectedNode2 = genericNodeFactory({
        label: "ConnectedNode2",
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode1],
        [connectedNode1, connectedNode2],
      ]);
    });

    it("should identify simple disconnected graph", async () => {
      const connectedNode = genericNodeFactory({
        label: "ConnectedNode",
      });

      const disconnectedNode1 = genericNodeFactory({
        label: "DisconnectedNode1",
      });

      const disconnectedNode2 = genericNodeFactory({
        label: "DisconnectedNode2",
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [disconnectedNode1, disconnectedNode2],
      ]);
    });

    it("should identify multiple disconnected graphs", async () => {
      const connectedNode = genericNodeFactory({
        label: "ConnectedNode",
      });

      const disconnectedNode1 = genericNodeFactory({
        label: "DisconnectedNode1",
      });

      const disconnectedNode2 = genericNodeFactory({
        label: "DisconnectedNode2",
      });

      const disconnectedNode3 = genericNodeFactory({
        label: "DisconnectedNode3",
      });

      const disconnectedNode4 = genericNodeFactory({
        label: "DisconnectedNode4",
      });

      const disconnectedNode5 = genericNodeFactory({
        label: "DisconnectedNode5",
      });

      const disconnectedNode6 = genericNodeFactory({
        label: "DisconnectedNode6",
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [disconnectedNode1, disconnectedNode2],
        [disconnectedNode1, disconnectedNode3],
        [disconnectedNode4, disconnectedNode5],
        [disconnectedNode5, disconnectedNode6],
      ]);
    });

    it("should identify multiple disconnected graphs with flipped edges", async () => {
      const connectedNode = genericNodeFactory({
        label: "ConnectedNode",
      });

      const disconnectedNode1 = genericNodeFactory({
        label: "DisconnectedNode1",
      });

      const disconnectedNode2 = genericNodeFactory({
        label: "DisconnectedNode2",
      });

      const disconnectedNode3 = genericNodeFactory({
        label: "DisconnectedNode3",
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [disconnectedNode2, disconnectedNode3],
        [disconnectedNode1, disconnectedNode2],
      ]);
    });

    it("should handle circular graphs", async () => {
      const connectedNode = genericNodeFactory({
        label: "ConnectedNode",
      });

      const disconnectedNode1 = genericNodeFactory({
        label: "DisconnectedNode1",
      });

      const disconnectedNode2 = genericNodeFactory({
        label: "DisconnectedNode2",
      });

      const disconnectedNode3 = genericNodeFactory({
        label: "DisconnectedNode3",
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [disconnectedNode1, disconnectedNode2],
        [disconnectedNode2, disconnectedNode3],
        [disconnectedNode3, disconnectedNode1],
      ]);
    });

    it("should handle conditional node with prompt nodes in different ports in unused graphs", async () => {
      const connectedNode = genericNodeFactory({
        label: "ConnectedNode",
      });

      // Create a conditional node with if/else ports
      const conditionalNode = conditionalNodeFactory({
        label: "ConditionalNode",
        includeElif: false, // Only if and else ports
      }).build();

      // Create prompt nodes for different ports
      const promptNode1 = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
      }).build();
      promptNode1.id = "prompt-node-1";
      promptNode1.data.sourceHandleId = "prompt-1-source";
      promptNode1.data.targetHandleId = "prompt-1-target";

      const promptNode2 = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
      }).build();
      promptNode2.id = "prompt-node-2";
      promptNode2.data.sourceHandleId = "prompt-2-source";
      promptNode2.data.targetHandleId = "prompt-2-target";

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [[conditionalNode, "0"], promptNode1], // if port -> prompt node 1
        [[conditionalNode, "1"], promptNode2], // else port -> prompt node 2
      ]);
    });
  });
});
