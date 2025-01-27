import { Writer } from "@fern-api/python-ast/core/Writer";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { afterEach, vi } from "vitest";

import { workflowContextFactory } from "./helpers";
import { inputVariableContextFactory } from "./helpers/input-variable-context-factory";
import {
  entrypointNodeDataFactory,
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
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }, 1000000);
  });
});
