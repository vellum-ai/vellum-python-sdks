import { Writer } from "@fern-api/python-ast/core/Writer";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { afterEach, vi } from "vitest";

import { workflowContextFactory } from "./helpers";
import { inputVariableContextFactory } from "./helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  entrypointNodeDataFactory,
  mergeNodeDataFactory,
  searchNodeDataFactory,
  templatingNodeFactory,
  terminalNodeDataFactory,
} from "./helpers/node-data-factories";

import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { workflowOutputContextFactory } from "src/__test__/helpers/workflow-output-context-factory";
import * as codegen from "src/codegen";
import { createNodeContext, WorkflowContext } from "src/context";
import { WorkflowEdge } from "src/types/vellum";

describe("Workflow", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  const moduleName = "test";
  const entrypointNode = entrypointNodeDataFactory();

  beforeEach(async () => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );

    workflowContext = workflowContextFactory();
    workflowContext.addEntrypointNode(entrypointNode);

    const nodeData = terminalNodeDataFactory();
    await createNodeContext({
      workflowContext: workflowContext,
      nodeData,
    });

    writer = new Writer();
  });

  afterEach(async () => {
    vi.restoreAllMocks();
  });

  describe("write", () => {
    it("should generate correct code when there are input variables", async () => {
      const inputs = codegen.inputs({ workflowContext });
      const workflow = codegen.workflow({
        moduleName,
        workflowContext,
        inputs,
        nodes: [],
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when there are no input variables", async () => {
      const inputs = codegen.inputs({ workflowContext });
      const workflow = codegen.workflow({
        moduleName,
        workflowContext,
        inputs,
        nodes: [],
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code with Search Results as an output variable", async () => {
      workflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: {
            id: "input-variable-id",
            key: "query",
            type: "STRING",
          },
          workflowContext,
        })
      );

      const inputs = codegen.inputs({ workflowContext });

      workflowContext.addWorkflowOutputContext(
        workflowOutputContextFactory({ workflowContext })
      );

      const workflow = codegen.workflow({
        moduleName,
        workflowContext,
        inputs,
        nodes: [],
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle edges pointing to non-existent nodes", async () => {
      workflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: {
            id: "input-variable-id",
            key: "query",
            type: "STRING",
          },
          workflowContext,
        })
      );

      const inputs = codegen.inputs({ workflowContext });

      const searchNodeData = searchNodeDataFactory();
      await createNodeContext({
        workflowContext: workflowContext,
        nodeData: searchNodeData,
      });

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: searchNodeData.id,
          targetHandleId: searchNodeData.data.sourceHandleId,
        },
        {
          id: "edge-2",
          type: "DEFAULT",
          sourceNodeId: searchNodeData.id,
          sourceHandleId: "some-handle",
          targetNodeId: "non-existent-node-id",
          targetHandleId: "some-target-handle",
        },
      ];

      workflowContext.addWorkflowEdges(edges);

      const workflow = codegen.workflow({
        moduleName,
        workflowContext,
        inputs,
        nodes: [searchNodeData],
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle the case of multiple nodes with the same label", async () => {
      const templatingNodeData1 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf80",
        label: "Templating Node",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb98",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2948",
      });
      await createNodeContext({
        workflowContext: workflowContext,
        nodeData: templatingNodeData1,
      });

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      });
      await createNodeContext({
        workflowContext: workflowContext,
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

      const inputs = codegen.inputs({ workflowContext });
      const workflow = codegen.workflow({
        moduleName,
        workflowContext,
        inputs,
        nodes: [templatingNodeData1, templatingNodeData2],
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }, 1000000);

    describe("graph", () => {
      it("should be correct for a basic single node case", async () => {
        workflowContext.addInputVariableContext(
          inputVariableContextFactory({
            inputVariableData: {
              id: "input-variable-id",
              key: "query",
              type: "STRING",
            },
            workflowContext,
          })
        );

        const inputs = codegen.inputs({ workflowContext });

        workflowContext.addWorkflowOutputContext(
          workflowOutputContextFactory({ workflowContext })
        );

        const searchNodeData = searchNodeDataFactory();
        await createNodeContext({
          workflowContext: workflowContext,
          nodeData: searchNodeData,
        });

        const edges: WorkflowEdge[] = [
          {
            id: "edge-1",
            type: "DEFAULT",
            sourceNodeId: entrypointNode.id,
            sourceHandleId: entrypointNode.data.sourceHandleId,
            targetNodeId: searchNodeData.id,
            targetHandleId: searchNodeData.data.sourceHandleId,
          },
        ];
        workflowContext.addWorkflowEdges(edges);

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [searchNodeData],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic multiple nodes case", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [templatingNodeData1, templatingNodeData2],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for three nodes", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic single edge case", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [templatingNodeData1, templatingNodeData2],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic merge node case", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [templatingNodeData1, templatingNodeData2, mergeNodeData],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic merge node case of multiple nodes", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
            mergeNodeData,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic merge node and an additional edge", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            mergeNodeData,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic merge between a node and an edge", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            mergeNodeData,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a basic conditional node case", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            conditionalNodeData,
            templatingNodeData1,
            templatingNodeData2,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a longer branch", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for set of a branch and a node", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a node to a set", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a node to a set to a node", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
            templatingNodeData4,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for set of a branch and a node to a node", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
            templatingNodeData4,
            templatingNodeData5,
            mergeNodeData,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a single port pointing to a set", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            conditionalNodeData,
            templatingNodeData1,
            templatingNodeData2,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for port within set to a set", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            conditionalNodeData,
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for a nested conditional node within a set", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            conditionalNodeData,
            conditionalNode2Data,
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
            templatingNodeData4,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for two branches merging from sets", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [
            conditionalNodeData,
            templatingNodeData1,
            templatingNodeData2,
            templatingNodeData3,
            templatingNodeData4,
            templatingNodeData5,
          ],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it("should be correct for two branches from the same node", async () => {
        const inputs = codegen.inputs({ workflowContext });

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

        const workflow = codegen.workflow({
          moduleName,
          workflowContext,
          inputs,
          nodes: [templatingNodeData1, templatingNodeData2, mergeNodeData],
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });
    });
  });
});
