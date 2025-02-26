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
import { WorkflowDataNode } from "src/types/vellum";

describe("Workflow", () => {
  const entrypointNode = entrypointNodeDataFactory();
  describe("unused_graphs", () => {
    const runUnusedGraphsWorkflowTest = async (
      edges: EdgeFactoryNodePair[]
    ) => {
      const workflowContext = workflowContextFactory();
      const writer = new Writer();
      workflowContext.addEntrypointNode(entrypointNode);

      const nodes = Array.from(
        new Set(
          edges
            .flatMap(([source, target]) => [
              Array.isArray(source) ? source[0] : source,
              Array.isArray(target) ? target[0] : target,
            ])
            .filter(
              (node): node is WorkflowDataNode => node.type !== "ENTRYPOINT"
            )
        )
      );

      await Promise.all(
        nodes.map((node) => {
          createNodeContext({
            workflowContext,
            nodeData: node,
          });
        })
      );

      workflowContext.addWorkflowEdges(edgesFactory(edges));

      const inputs = codegen.inputs({ workflowContext });
      const workflow = codegen.workflow({
        moduleName: "test",
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
