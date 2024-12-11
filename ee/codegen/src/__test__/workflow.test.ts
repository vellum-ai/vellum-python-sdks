import { Writer } from "@fern-api/python-ast/core/Writer";

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
    workflowContext = workflowContextFactory({
      workflowClassName: "TestWorkflow",
    });
    workflowContext.addEntrypointNode(entrypointNode);

    const nodeData = terminalNodeDataFactory();
    workflowContext.addNodeContext(
      await createNodeContext({
        workflowContext: workflowContext,
        nodeData,
      })
    );

    writer = new Writer();
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

      workflowContext.addWorkflowOutputContext(workflowOutputContextFactory());

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
      const searchNodeContext = await createNodeContext({
        workflowContext: workflowContext,
        nodeData: searchNodeData,
      });
      workflowContext.addNodeContext(searchNodeContext);

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
          workflowOutputContextFactory()
        );

        const searchNodeData = searchNodeDataFactory();
        const searchNodeContext = await createNodeContext({
          workflowContext: workflowContext,
          nodeData: searchNodeData,
        });
        workflowContext.addNodeContext(searchNodeContext);

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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

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

      it("should be correct for a basic single edge case", async () => {
        const inputs = codegen.inputs({ workflowContext });

        const templatingNodeData1 = templatingNodeFactory();
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const mergeNodeData = mergeNodeDataFactory();
        const mergeNodeContext = await createNodeContext({
          workflowContext,
          nodeData: mergeNodeData,
        });
        workflowContext.addNodeContext(mergeNodeContext);
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

      it("should be correct for a basic merge node and an additional edge", async () => {
        const inputs = codegen.inputs({ workflowContext });

        const templatingNodeData1 = templatingNodeFactory();
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

        const mergeNodeData = mergeNodeDataFactory();
        const mergeNodeContext = await createNodeContext({
          workflowContext,
          nodeData: mergeNodeData,
        });
        workflowContext.addNodeContext(mergeNodeContext);
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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

        const mergeNodeData = mergeNodeDataFactory();
        const mergeNodeContext = await createNodeContext({
          workflowContext,
          nodeData: mergeNodeData,
        });
        workflowContext.addNodeContext(mergeNodeContext);
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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const conditionalNodeData = conditionalNodeFactory();
        const conditionalNodeContext = await createNodeContext({
          workflowContext,
          nodeData: conditionalNodeData,
        });
        workflowContext.addNodeContext(conditionalNodeContext);
        const conditionalSourceHandle1 =
          conditionalNodeData.data.conditions[0]?.sourceHandleId;
        const conditionalSourceHandle2 =
          conditionalNodeData.data.conditions[1]?.sourceHandleId;
        if (!conditionalSourceHandle1 || !conditionalSourceHandle2) {
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
            sourceHandleId: conditionalSourceHandle1,
            targetNodeId: templatingNodeData1.id,
            targetHandleId: templatingNodeData1.data.targetHandleId,
          },
          {
            id: "edge-3",
            type: "DEFAULT",
            sourceNodeId: conditionalNodeData.id,
            sourceHandleId: conditionalSourceHandle2,
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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

        const templatingNodeData4 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
          label: "Templating Node 4",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
        });
        const templatingNodeContext4 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData4,
        });
        workflowContext.addNodeContext(templatingNodeContext4);

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
        const templatingNodeContext1 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData1,
        });
        workflowContext.addNodeContext(templatingNodeContext1);

        const templatingNodeData2 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
          label: "Templating Node 2",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
        });
        const templatingNodeContext2 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData2,
        });
        workflowContext.addNodeContext(templatingNodeContext2);

        const templatingNodeData3 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf82",
          label: "Templating Node 3",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9a",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294a",
        });
        const templatingNodeContext3 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData3,
        });
        workflowContext.addNodeContext(templatingNodeContext3);

        const templatingNodeData4 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf83",
          label: "Templating Node 4",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9b",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294b",
        });
        const templatingNodeContext4 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData4,
        });
        workflowContext.addNodeContext(templatingNodeContext4);

        const templatingNodeData5 = templatingNodeFactory({
          id: "7e09927b-6d6f-4829-92c9-54e66bdcaf84",
          label: "Templating Node 5",
          sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb9c",
          targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a294c",
        });
        const templatingNodeContext5 = await createNodeContext({
          workflowContext,
          nodeData: templatingNodeData5,
        });
        workflowContext.addNodeContext(templatingNodeContext5);

        const mergeNodeData = mergeNodeDataFactory();
        const mergeNodeContext = await createNodeContext({
          workflowContext,
          nodeData: mergeNodeData,
        });
        workflowContext.addNodeContext(mergeNodeContext);
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
    });
  });
});
