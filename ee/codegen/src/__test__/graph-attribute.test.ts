import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "./helpers";
import { edgesFactory } from "./helpers/edge-data-factories";
import {
  conditionalNodeFactory,
  entrypointNodeDataFactory,
  finalOutputNodeFactory,
  mergeNodeDataFactory,
  templatingNodeFactory,
} from "./helpers/node-data-factories";

import { createNodeContext, WorkflowContext } from "src/context";
import { GraphAttribute } from "src/generators/graph-attribute";
import { WorkflowEdge } from "src/types/vellum";

describe("Workflow", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  const entrypointNode = entrypointNodeDataFactory();

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    workflowContext.addEntrypointNode(entrypointNode);

    writer = new Writer();
  });

  describe("graph", () => {
    it("should be correct for a basic single node case", async () => {
      const templatingNodeData = templatingNodeFactory();
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData,
      });

      workflowContext.addWorkflowEdges(
        edgesFactory([[entrypointNode, templatingNodeData]])
      );

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a basic multiple nodes case", async () => {
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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for three nodes", async () => {
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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a basic single edge case", async () => {
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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a basic merge node case", async () => {
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
      const mergeTargetHandle1 = mergeNodeData.data.targetHandles[0]?.id;
      const mergeTargetHandle2 = mergeNodeData.data.targetHandles[1]?.id;
      if (!mergeTargetHandle1 || !mergeTargetHandle2) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle1,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a basic merge node case of multiple nodes", async () => {
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

      const mergeNodeData = mergeNodeDataFactory();
      await createNodeContext({
        workflowContext,
        nodeData: mergeNodeData,
      });
      const mergeTargetHandle1 = mergeNodeData.data.targetHandles[0]?.id;
      const mergeTargetHandle2 = mergeNodeData.data.targetHandles[1]?.id;
      if (!mergeTargetHandle1 || !mergeTargetHandle2) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle1,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
        {
          id: "edge-6",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData3.id,
          sourceHandleId: templatingNodeData3.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a basic merge node and an additional edge", async () => {
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

      const mergeNodeData = mergeNodeDataFactory();
      await createNodeContext({
        workflowContext,
        nodeData: mergeNodeData,
      });
      const mergeTargetHandle1 = mergeNodeData.data.targetHandles[0]?.id;
      const mergeTargetHandle2 = mergeNodeData.data.targetHandles[1]?.id;
      if (!mergeTargetHandle1 || !mergeTargetHandle2) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle1,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: mergeNodeData.id,
          sourceHandleId: mergeNodeData.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should be correct for a basic merge between a node and an edge", async () => {
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

      const mergeNodeData = mergeNodeDataFactory();
      await createNodeContext({
        workflowContext,
        nodeData: mergeNodeData,
      });
      const mergeTargetHandle1 = mergeNodeData.data.targetHandles[0]?.id;
      const mergeTargetHandle2 = mergeNodeData.data.targetHandles[1]?.id;
      if (!mergeTargetHandle1 || !mergeTargetHandle2) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle1,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData3.id,
          sourceHandleId: templatingNodeData3.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
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
      const conditionalIfSourceHandleId =
        conditionalNodeData.data.conditions[0]?.sourceHandleId;
      const conditionalElseSourceHandleId =
        conditionalNodeData.data.conditions[1]?.sourceHandleId;
      if (!conditionalIfSourceHandleId || !conditionalElseSourceHandleId) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: conditionalNodeData.id,
          targetHandleId: conditionalNodeData.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalIfSourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalElseSourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData3.id,
          sourceHandleId: templatingNodeData3.data.sourceHandleId,
          targetNodeId: templatingNodeData4.id,
          targetHandleId: templatingNodeData4.data.targetHandleId,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: templatingNodeData4.id,
          targetHandleId: templatingNodeData4.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
      const mergeTargetHandle1 = mergeNodeData.data.targetHandles[0]?.id;
      const mergeTargetHandle2 = mergeNodeData.data.targetHandles[1]?.id;
      if (!mergeTargetHandle1 || !mergeTargetHandle2) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData3.id,
          sourceHandleId: templatingNodeData3.data.sourceHandleId,
          targetNodeId: templatingNodeData4.id,
          targetHandleId: templatingNodeData4.data.targetHandleId,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData4.id,
          sourceHandleId: templatingNodeData4.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle1,
        },
        {
          id: "edge-6",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
        {
          id: "edge-7",
          type: "DEFAULT",
          sourceNodeId: mergeNodeData.id,
          sourceHandleId: mergeNodeData.data.sourceHandleId,
          targetNodeId: templatingNodeData5.id,
          targetHandleId: templatingNodeData5.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
      const conditionalIfSourceHandleId =
        conditionalNodeData.data.conditions[0]?.sourceHandleId;
      const conditionalElseSourceHandleId =
        conditionalNodeData.data.conditions[1]?.sourceHandleId;
      if (!conditionalIfSourceHandleId || !conditionalElseSourceHandleId) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: conditionalNodeData.id,
          targetHandleId: conditionalNodeData.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalIfSourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalIfSourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
      const conditionalIfSourceHandleId =
        conditionalNodeData.data.conditions[0]?.sourceHandleId;
      const conditionalElseSourceHandleId =
        conditionalNodeData.data.conditions[1]?.sourceHandleId;
      if (!conditionalIfSourceHandleId || !conditionalElseSourceHandleId) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: conditionalNodeData.id,
          targetHandleId: conditionalNodeData.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalIfSourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalElseSourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalElseSourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
      const conditionalIfSourceHandleId =
        conditionalNodeData.data.conditions[0]?.sourceHandleId;
      const conditionalElseSourceHandleId =
        conditionalNodeData.data.conditions[1]?.sourceHandleId;
      if (!conditionalIfSourceHandleId || !conditionalElseSourceHandleId) {
        throw new Error("Handle IDs are required");
      }

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
      const conditional2IfSourceHandleId =
        conditionalNode2Data.data.conditions[0]?.sourceHandleId;
      const conditional2ElseSourceHandleId =
        conditionalNode2Data.data.conditions[1]?.sourceHandleId;
      if (!conditional2IfSourceHandleId || !conditional2ElseSourceHandleId) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: conditionalNodeData.id,
          targetHandleId: conditionalNodeData.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalIfSourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalElseSourceHandleId,
          targetNodeId: conditionalNode2Data.id,
          targetHandleId: conditionalNode2Data.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalElseSourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: conditionalNode2Data.id,
          sourceHandleId: conditional2ElseSourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-6",
          type: "DEFAULT",
          sourceNodeId: conditionalNode2Data.id,
          sourceHandleId: conditional2ElseSourceHandleId,
          targetNodeId: templatingNodeData4.id,
          targetHandleId: templatingNodeData4.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
      const conditionalIfSourceHandleId =
        conditionalNodeData.data.conditions[0]?.sourceHandleId;
      const conditionalElseSourceHandleId =
        conditionalNodeData.data.conditions[1]?.sourceHandleId;
      if (!conditionalIfSourceHandleId || !conditionalElseSourceHandleId) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: conditionalNodeData.id,
          targetHandleId: conditionalNodeData.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalIfSourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: conditionalNodeData.id,
          sourceHandleId: conditionalElseSourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-5",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: templatingNodeData3.id,
          targetHandleId: templatingNodeData3.data.targetHandleId,
        },
        {
          id: "edge-6",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData3.id,
          sourceHandleId: templatingNodeData3.data.sourceHandleId,
          targetNodeId: templatingNodeData4.id,
          targetHandleId: templatingNodeData4.data.targetHandleId,
        },
        {
          id: "edge-7",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData5.id,
          targetHandleId: templatingNodeData5.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
      const mergeTargetHandle1 = mergeNodeData.data.targetHandles[0]?.id;
      const mergeTargetHandle2 = mergeNodeData.data.targetHandles[1]?.id;
      if (!mergeTargetHandle1 || !mergeTargetHandle2) {
        throw new Error("Handle IDs are required");
      }

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle1,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData2.id,
          sourceHandleId: templatingNodeData2.data.sourceHandleId,
          targetNodeId: mergeNodeData.id,
          targetHandleId: mergeTargetHandle2,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: templatingNodeData1.id,
          sourceHandleId: templatingNodeData1.data.sourceHandleId,
          targetNodeId: templatingNodeData2.id,
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: topNode.id,
          targetHandleId: topNode.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: topNode.id,
          sourceHandleId: topNode.data.sourceHandleId,
          targetNodeId: outputTopNode.id,
          targetHandleId: outputTopNode.data.targetHandleId,
        },
        {
          id: "edge-3",
          type: "DEFAULT",
          sourceNodeId: topNode.id,
          sourceHandleId: topNode.data.sourceHandleId,
          targetNodeId: outputMiddleNode.id,
          targetHandleId: outputMiddleNode.data.targetHandleId,
        },
        {
          id: "edge-4",
          type: "DEFAULT",
          sourceNodeId: topNode.id,
          sourceHandleId: topNode.data.sourceHandleId,
          targetNodeId: outputBottomNode.id,
          targetHandleId: outputBottomNode.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

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
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node 2",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext,
        nodeData: templatingNodeData2,
      });

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: "non-existent-node-id",
          targetHandleId: templatingNodeData2.data.targetHandleId,
        },
      ];
      workflowContext.addWorkflowEdges(edges);

      new GraphAttribute({ workflowContext }).write(writer);
      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toContain(
        `Failed to find target node with ID 'non-existent-node-id' referenced from edge edge-2`
      );
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
