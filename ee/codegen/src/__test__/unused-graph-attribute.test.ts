import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";

import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  templatingNodeFactory,
  entrypointNodeDataFactory,
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
      const connectedNode1 = templatingNodeFactory();
      const connectedNode2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode1],
        [connectedNode1, connectedNode2],
      ]);
    });

    it("should identify simple disconnected graph", async () => {
      const connectedNode = templatingNodeFactory();

      const disconnectedNode1 = templatingNodeFactory({
        id: uuidv4(),
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const disconnectedNode2 = templatingNodeFactory({
        id: uuidv4(),
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [disconnectedNode1, disconnectedNode2],
      ]);
    });

    it("should identify multiple disconnected graphs", async () => {
      const connectedNode = templatingNodeFactory();

      const disconnectedNode1 = templatingNodeFactory({
        id: uuidv4(),
        label: "Disconnected Node 1",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const disconnectedNode2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Disconnected Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const disconnectedNode3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Disconnected Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const disconnectedNode4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Disconnected Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const disconnectedNode5 = templatingNodeFactory({
        id: uuidv4(),
        label: "Disconnected Node 5",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const disconnectedNode6 = templatingNodeFactory({
        id: uuidv4(),
        label: "Disconnected Node 6",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runUnusedGraphsWorkflowTest([
        [entrypointNode, connectedNode],
        [disconnectedNode1, disconnectedNode2],
        [disconnectedNode1, disconnectedNode3],
        [disconnectedNode4, disconnectedNode5],
        [disconnectedNode5, disconnectedNode6],
      ]);
    });
  });
});
