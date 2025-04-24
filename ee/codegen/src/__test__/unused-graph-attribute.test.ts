import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  entrypointNodeDataFactory,
  genericNodeFactory,
} from "./helpers/node-data-factories";

import * as codegen from "src/codegen";
import { createNodeContext } from "src/context";

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

      const inputs = codegen.inputs({ workflowContext });
      const workflow = codegen.workflow({
        workflowContext,
        inputs,
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
  });
});
