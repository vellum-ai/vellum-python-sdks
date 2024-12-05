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
      it.each([[true], [false]])(
        "should be correct for a basic single node case",
        async (breadthFirstGraphGeneration) => {
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
            breadthFirstGraphGeneration,
          });

          workflow.getWorkflowFile().write(writer);
          expect(await writer.toStringFormatted()).toMatchSnapshot();
        }
      );

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
          // This test case fails with the legacy graph generation algorithm
          // so we don't parameterize over it.
          breadthFirstGraphGeneration: true,
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it.each([[true], [false]])(
        "should be correct for a basic single edge case",
        async (breadthFirstGraphGeneration) => {
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
            breadthFirstGraphGeneration,
          });

          workflow.getWorkflowFile().write(writer);
          expect(await writer.toStringFormatted()).toMatchSnapshot();
        }
      );

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
          // This test case fails with the legacy graph generation algorithm
          // so we don't parameterize over it.
          breadthFirstGraphGeneration: true,
        });

        workflow.getWorkflowFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });

      it.each([[true], [false]])(
        "should be correct for a basic conditional node case",
        async (breadthFirstGraphGeneration) => {
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
            breadthFirstGraphGeneration,
          });

          workflow.getWorkflowFile().write(writer);
          expect(await writer.toStringFormatted()).toMatchSnapshot();
        }
      );
    });
  });
});
