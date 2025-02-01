import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";

import { workflowContextFactory } from "./helpers";
import {
  EdgeFactoryNodePair,
  edgesFactory,
} from "./helpers/edge-data-factories";
import {
  conditionalNodeFactory,
  entrypointNodeDataFactory,
  finalOutputNodeFactory,
  mergeNodeDataFactory,
  templatingNodeFactory,
} from "./helpers/node-data-factories";

import { WorkflowContext, createNodeContext } from "src/context";
import { GraphAttribute } from "src/generators/graph-attribute";
import { WorkflowDataNode } from "src/types/vellum";

describe("Workflow", () => {
  const entrypointNode = entrypointNodeDataFactory();
  const runGraphTest = async (edges: EdgeFactoryNodePair[]) => {
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

    new GraphAttribute({ workflowContext }).write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  };

  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    workflowContext.addEntrypointNode(entrypointNode);
    writer = new Writer();
  });

  describe("graph", () => {
    it("should be correct for a basic single node case", async () => {
      const templatingNodeData = templatingNodeFactory();

      await runGraphTest([[entrypointNode, templatingNodeData]]);
    });

    it("should be correct for a basic multiple nodes case", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
      ]);
    });

    it("should be correct for three nodes", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [entrypointNode, templatingNodeData3],
      ]);
    });

    it("should be correct for a basic single edge case", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
      ]);
    });

    it("should be correct for a basic merge node case", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const mergeNodeData = mergeNodeDataFactory();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
      ]);
    });

    it("should be correct for a basic merge node case of multiple nodes", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const mergeNodeData = mergeNodeDataFactory(3);

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [entrypointNode, templatingNodeData3],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [templatingNodeData3, [mergeNodeData, 2]],
      ]);
    });

    it("should be correct for a basic merge node and an additional edge", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const mergeNodeData = mergeNodeDataFactory();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [mergeNodeData, templatingNodeData3],
      ]);
    });

    it("should be correct for a basic merge between a node and an edge", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const mergeNodeData = mergeNodeDataFactory();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData2, [mergeNodeData, 0]],
        [templatingNodeData3, [mergeNodeData, 1]],
      ]);
    });

    it("should be correct for a basic conditional node case", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const conditionalNodeData = conditionalNodeFactory();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], templatingNodeData2],
      ]);
    });

    it("should be correct for a longer branch", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [templatingNodeData2, templatingNodeData3],
      ]);
    });

    it("should be correct for set of a branch and a node", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [entrypointNode, templatingNodeData3],
      ]);
    });

    it("should be correct for a node to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
      ]);
    });

    it("should be correct for a node to a set to a node", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData3, templatingNodeData4],
        [templatingNodeData2, templatingNodeData4],
      ]);
    });

    it("should be correct for set of a branch and a node to a node", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData5 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 5",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const mergeNodeData = mergeNodeDataFactory();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [entrypointNode, templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData3, templatingNodeData4],
        [templatingNodeData4, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [mergeNodeData, templatingNodeData5],
      ]);
    });

    it("should be correct for a single port pointing to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const conditionalNodeData = conditionalNodeFactory();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "0"], templatingNodeData2],
      ]);
    });

    it("should be correct for port within set to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const conditionalNodeData = conditionalNodeFactory();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], templatingNodeData2],
        [[conditionalNodeData, "1"], templatingNodeData3],
      ]);
    });

    it("should be correct for a nested conditional node within a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const conditionalNodeData = conditionalNodeFactory();

      const conditionalNode2Data = conditionalNodeFactory({
        id: uuidv4(),
        label: "Conditional Node 2",
        targetHandleId: uuidv4(),
        ifSourceHandleId: uuidv4(),
        elseSourceHandleId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], conditionalNode2Data],
        [[conditionalNodeData, "1"], templatingNodeData2],
        [[conditionalNode2Data, "1"], templatingNodeData3],
        [[conditionalNode2Data, "1"], templatingNodeData4],
      ]);
    });

    it("should be correct for two branches merging from sets", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 3",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 4",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const templatingNodeData5 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 5",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const conditionalNodeData = conditionalNodeFactory();

      await runGraphTest([
        [entrypointNode, conditionalNodeData],
        [[conditionalNodeData, "0"], templatingNodeData1],
        [[conditionalNodeData, "1"], templatingNodeData2],
        [templatingNodeData1, templatingNodeData3],
        [templatingNodeData2, templatingNodeData3],
        [templatingNodeData3, templatingNodeData4],
        [templatingNodeData1, templatingNodeData5],
      ]);
    });

    it("should be correct for two branches from the same node", async () => {
      const templatingNodeData1 = templatingNodeFactory();

      const templatingNodeData2 = templatingNodeFactory({
        id: uuidv4(),
        label: "Templating Node 2",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const mergeNodeData = mergeNodeDataFactory();

      await runGraphTest([
        [entrypointNode, templatingNodeData1],
        [templatingNodeData1, [mergeNodeData, 0]],
        [templatingNodeData2, [mergeNodeData, 1]],
        [templatingNodeData1, templatingNodeData2],
      ]);
    });

    it("should define nested sets of nodes without compilation errors", async () => {
      const topNode = templatingNodeFactory({ label: "Top Node" });

      const outputTopNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Output Top Node",
        name: "output-top-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      });

      const outputMiddleNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Output Middle Node",
        name: "output-middle-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      });

      const outputBottomNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Output Bottom Node",
        name: "output-bottom-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      });

      await runGraphTest([
        [entrypointNode, topNode],
        [topNode, outputTopNode],
        [topNode, outputMiddleNode],
        [topNode, outputBottomNode],
      ]);
    });

    it("should show errors for a node pointing to non-existent node", async () => {
      // We skip using runGraphTest here because we want to test an error case

      workflowContext = workflowContextFactory({ strict: false });
      workflowContext.addEntrypointNode(entrypointNode);
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "non-existent-node-id",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      // No node context created

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [entrypointNode, templatingNodeData2],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toContain(
        `Failed to find target node with ID 'non-existent-node-id' referenced from edge edge-2`
      );
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should support an edge between two sets", async () => {
      const topLeftNode = templatingNodeFactory({ label: "Top Left Node" });

      const topRightNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Top Right Node",
        name: "top-right-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      });

      const bottomLeftNode = templatingNodeFactory({
        id: uuidv4(),
        label: "Bottom Left Node",
        sourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      });

      const bottomRightNode = finalOutputNodeFactory({
        id: uuidv4(),
        label: "Bottom Right Node",
        name: "bottom-right-node",
        targetHandleId: uuidv4(),
        outputId: uuidv4(),
      });

      /**
       * Currently the snapshot generated for this test is suboptimal. Ideally, we would generate:
       *
       * {
       *     TopLeftNode,
       *     BottomLeftNode,
       * } >> Graph.from_set(
       *     {
       *         TopRightNode,
       *         BottomRightNode,
       *     }
       * )
       */
      await runGraphTest([
        [entrypointNode, topLeftNode],
        [entrypointNode, bottomLeftNode],
        [topLeftNode, topRightNode],
        [bottomLeftNode, topRightNode],
        [topLeftNode, bottomRightNode],
        [bottomLeftNode, bottomRightNode],
      ]);
    });
  });
});
