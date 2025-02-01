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
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const conditionalNodeData = conditionalNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: conditionalNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, conditionalNodeData],
          [[conditionalNodeData, "0"], templatingNodeData1],
          [[conditionalNodeData, "1"], templatingNodeData2],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a longer branch", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [templatingNodeData1, templatingNodeData2],
          [templatingNodeData2, templatingNodeData3],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for set of a branch and a node", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [templatingNodeData1, templatingNodeData2],
          [entrypointNode, templatingNodeData3],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a node to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [templatingNodeData1, templatingNodeData2],
          [templatingNodeData1, templatingNodeData3],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a node to a set to a node", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
        label: "Templating Node 4",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData4,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [templatingNodeData1, templatingNodeData2],
          [templatingNodeData1, templatingNodeData3],
          [templatingNodeData3, templatingNodeData4],
          [templatingNodeData2, templatingNodeData4],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for set of a branch and a node to a node", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
        label: "Templating Node 4",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData4,
      });

      const templatingNodeData5 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf84",
        label: "Templating Node 5",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9c",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294c",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData5,
      });

      const mergeNodeData = mergeNodeDataFactory();
      await createNodeContext({
        workflowContext,
        nodeData: mergeNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [entrypointNode, templatingNodeData2],
          [templatingNodeData1, templatingNodeData3],
          [templatingNodeData3, templatingNodeData4],
          [templatingNodeData4, [mergeNodeData, 0]],
          [templatingNodeData2, [mergeNodeData, 1]],
          [mergeNodeData, templatingNodeData5],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a single port pointing to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const conditionalNodeData = conditionalNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: conditionalNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, conditionalNodeData],
          [[conditionalNodeData, "0"], templatingNodeData1],
          [[conditionalNodeData, "0"], templatingNodeData2],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for port within set to a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf84",
        label: "Templating Node 4",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9c",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294c",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData4,
      });

      const conditionalNodeData = conditionalNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: conditionalNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, conditionalNodeData],
          [[conditionalNodeData, "0"], templatingNodeData1],
          [[conditionalNodeData, "1"], templatingNodeData2],
          [[conditionalNodeData, "1"], templatingNodeData3],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a nested conditional node within a set", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf84",
        label: "Templating Node 4",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9c",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294c",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData4,
      });

      const conditionalNodeData = conditionalNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: conditionalNodeData,
      });

      const conditionalNode2Data = conditionalNodeFactory({
        id: "b81a4453-7b80-41ea-bd55-c62df8878fd4",
        label: "Conditional Node 2",
        targetHandleId: "842b9dda-7977-47ad-a322-eb15b4c7069e",
        ifSourceHandleId: "63345ab5-1a4d-48a1-ad33-91bec41f92a6",
        elseSourceHandleId: "14a8b603-6039-4491-92d4-868a4dae4c16",
      });
      await createNodeContext({
        workflowContext,
        nodeData: conditionalNode2Data,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, conditionalNodeData],
          [[conditionalNodeData, "0"], templatingNodeData1],
          [[conditionalNodeData, "1"], conditionalNode2Data],
          [[conditionalNodeData, "1"], templatingNodeData2],
          [[conditionalNode2Data, "1"], templatingNodeData3],
          [[conditionalNode2Data, "1"], templatingNodeData4],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for two branches merging from sets", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const templatingNodeData3 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
        label: "Templating Node 3",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData3,
      });

      const templatingNodeData4 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf84",
        label: "Templating Node 4",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9c",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294c",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData4,
      });

      const templatingNodeData5 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf85",
        label: "Templating Node 5",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9d",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294d",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData5,
      });

      const conditionalNodeData = conditionalNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: conditionalNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, conditionalNodeData],
          [[conditionalNodeData, "0"], templatingNodeData1],
          [[conditionalNodeData, "1"], templatingNodeData2],
          [templatingNodeData1, templatingNodeData3],
          [templatingNodeData2, templatingNodeData3],
          [templatingNodeData3, templatingNodeData4],
          [templatingNodeData1, templatingNodeData5],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for two branches from the same node", async () => {
      const templatingNodeData1 = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const mergeNodeData = mergeNodeDataFactory();
      await createNodeContext({
        workflowContext,
        nodeData: mergeNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, templatingNodeData1],
          [templatingNodeData1, [mergeNodeData, 0]],
          [templatingNodeData2, [mergeNodeData, 1]],
          [templatingNodeData1, templatingNodeData2],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should define nested sets of nodes without compilation errors", async () => {
      const topNode = templatingNodeFactory({ label: "Top Node" });
      await createNodeContext({
        workflowContext,
        nodeData: topNode,
      });

      const outputTopNode = finalOutputNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf86",
        label: "Output Top Node",
        name: "output-top-node",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294e",
        outputId: "7e09927b-6d6f-4829-92c9-54e66bdcaf86",
      });
      await createNodeContext({
        workflowContext,
        nodeData: outputTopNode,
      });

      const outputMiddleNode = finalOutputNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf87",
        label: "Output Middle Node",
        name: "output-middle-node",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294f",
        outputId: "7e09927b-6d6f-4829-92c9-54e66bdcaf87",
      });
      await createNodeContext({
        workflowContext,
        nodeData: outputMiddleNode,
      });

      const outputBottomNode = finalOutputNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf88",
        label: "Output Bottom Node",
        name: "output-bottom-node",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2950",
        outputId: "7e09927b-6d6f-4829-92c9-54e66bdcaf88",
      });
      await createNodeContext({
        workflowContext,
        nodeData: outputBottomNode,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, topNode],
          [topNode, outputTopNode],
          [topNode, outputMiddleNode],
          [topNode, outputBottomNode],
        ])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should show errors for a node pointing to non-existent node", async () => {
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
      await createNodeContext({
        workflowContext,
        nodeData: topLeftNode,
      });

      const topRightNode = finalOutputNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf86",
        label: "Top Right Node",
        name: "top-right-node",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294e",
        outputId: "7e09927b-6d6f-4829-92c9-54e66bdcaf86",
      });
      await createNodeContext({
        workflowContext,
        nodeData: topRightNode,
      });

      const bottomLeftNode = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf87",
        label: "Bottom Left Node",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });

      await createNodeContext({
        workflowContext,
        nodeData: bottomLeftNode,
      });

      const bottomRightNode = finalOutputNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf88",
        label: "Bottom Right Node",
        name: "bottom-right-node",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2950",
        outputId: "7e09927b-6d6f-4829-92c9-54e66bdcaf88",
      });
      await createNodeContext({
        workflowContext,
        nodeData: bottomRightNode,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([
          [entrypointNode, topLeftNode],
          [entrypointNode, bottomLeftNode],
          [topLeftNode, topRightNode],
          [bottomLeftNode, topRightNode],
          [topLeftNode, bottomRightNode],
          [bottomLeftNode, bottomRightNode],
        ])
      );

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
      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
