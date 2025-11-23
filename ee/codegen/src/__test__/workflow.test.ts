import { v4 as uuidv4 } from "uuid";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { afterEach, vi } from "vitest";

import { workflowContextFactory } from "./helpers";
import { edgesFactory } from "./helpers/edge-data-factories";
import { inputVariableContextFactory } from "./helpers/input-variable-context-factory";
import {
  conditionalNodeFactory,
  entrypointNodeDataFactory,
  finalOutputNodeFactory,
  searchNodeDataFactory,
  templatingNodeFactory,
  terminalNodeDataFactory,
} from "./helpers/node-data-factories";

import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { workflowOutputContextFactory } from "src/__test__/helpers/workflow-output-context-factory";
import * as codegen from "src/codegen";
import { createNodeContext, WorkflowContext } from "src/context";
import { OutputVariableContext } from "src/context/output-variable-context";
import { WorkflowOutputContext } from "src/context/workflow-output-context";
import { WorkflowGenerationError } from "src/generators/errors";
import { Writer } from "src/generators/extensions/writer";
import { GraphAttribute } from "src/generators/graph-attribute";
import { WorkflowEdge } from "src/types/vellum";

describe("Workflow", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  const entrypointNode = entrypointNodeDataFactory();

  beforeEach(async () => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );

    workflowContext = workflowContextFactory();

    const nodeData = terminalNodeDataFactory();
    await createNodeContext({
      workflowContext,
      nodeData,
    });

    writer = new Writer();
  });

  afterEach(async () => {
    vi.restoreAllMocks();
  });

  describe("write", () => {
    it("should generate correct code when there are input variables", async () => {
      const workflowContext = workflowContextFactory();
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
      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code when there are no input variables", async () => {
      const workflow = codegen.workflow({
        workflowContext,
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

      workflowContext.addOutputVariableContext(
        new OutputVariableContext({
          outputVariableData: {
            id: "output-id",
            key: "query",
            type: "STRING",
          },
          workflowContext,
        })
      );
      workflowContext.addWorkflowOutputContext(
        workflowOutputContextFactory({ workflowContext })
      );

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle edges pointing to non-existent nodes", async () => {
      const searchNodeData = searchNodeDataFactory().build();

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
      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes: [entrypointNode, searchNodeData],
          edges,
        },
      });

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

      await createNodeContext({
        workflowContext: workflowContext,
        nodeData: searchNodeData,
      });

      const workflow = codegen.workflow({
        workflowContext,
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
      }).build();

      const templatingNodeData2 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf81",
        label: "Templating Node",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb99",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2949",
      }).build();

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
      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes: [entrypointNode, templatingNodeData1, templatingNodeData2],
          edges,
        },
      });

      await createNodeContext({
        workflowContext: workflowContext,
        nodeData: templatingNodeData1,
      });

      await createNodeContext({
        workflowContext: workflowContext,
        nodeData: templatingNodeData2,
      });

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }, 1000000);

    it("should handle the workflow generation even if graph attribute fails in non-strict mode", async () => {
      vi.spyOn(
        GraphAttribute.prototype,
        "generateGraphMutableAst"
      ).mockImplementation(() => {
        throw new WorkflowGenerationError("test");
      });

      const templatingNodeData1 = templatingNodeFactory({
        id: "7e09927b-6d6f-4829-92c9-54e66bdcaf80",
        label: "Templating Node",
        sourceHandleId: "dd8397b1-5a41-4fa0-8c24-e5dffee4fb98",
        targetHandleId: "3feb7e71-ec63-4d58-82ba-c3df829a2948",
      }).build();

      const edges: WorkflowEdge[] = [
        {
          id: "edge-1",
          type: "DEFAULT",
          sourceNodeId: entrypointNode.id,
          sourceHandleId: entrypointNode.data.sourceHandleId,
          targetNodeId: templatingNodeData1.id,
          targetHandleId: templatingNodeData1.data.targetHandleId,
        },
      ];
      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes: [entrypointNode, templatingNodeData1],
          edges,
        },
        strict: false,
      });

      await createNodeContext({
        workflowContext: workflowContext,
        nodeData: templatingNodeData1,
      });

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle loops of conditionals and import Graph.from_set properly", async () => {
      const startNode = conditionalNodeFactory({
        label: "Start Node",
      }).build();

      const loopCheckNode = conditionalNodeFactory({
        id: uuidv4(),
        label: "Loop Check Node",
        ifSourceHandleId: uuidv4(),
        elseSourceHandleId: uuidv4(),
        targetHandleId: uuidv4(),
      }).build();

      const finalOutput = finalOutputNodeFactory().build();

      const topNode = templatingNodeFactory({
        label: "Top Node",
      }).build();

      const edges = edgesFactory([
        [entrypointNode, startNode],
        [[startNode, "0"], topNode],
        [[startNode, "1"], loopCheckNode],
        [[loopCheckNode, "0"], startNode],
        [[loopCheckNode, "1"], finalOutput],
        [[topNode, "0"], loopCheckNode],
      ]);

      const workflowContext = workflowContextFactory({
        workflowRawData: {
          nodes: [
            entrypointNode,
            startNode,
            loopCheckNode,
            finalOutput,
            topNode,
          ],
          edges,
        },
      });

      await createNodeContext({
        workflowContext,
        nodeData: startNode,
      });

      await createNodeContext({
        workflowContext,
        nodeData: loopCheckNode,
      });

      await createNodeContext({
        workflowContext,
        nodeData: finalOutput,
      });

      await createNodeContext({
        workflowContext,
        nodeData: topNode,
      });

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code with an output variable mapped to an input variable", async () => {
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

      workflowContext.addOutputVariableContext(
        new OutputVariableContext({
          outputVariableData: {
            id: "output-variable-id",
            key: "passthrough",
            type: "STRING",
          },
          workflowContext,
        })
      );

      workflowContext.addWorkflowOutputContext(
        new WorkflowOutputContext({
          workflowOutputValue: {
            outputVariableId: "output-variable-id",
            value: {
              type: "WORKFLOW_INPUT",
              inputVariableId: "input-variable-id",
            },
          },
          workflowContext,
        })
      );

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct display code when there are input variables with escape characters", async () => {
      workflowContext = workflowContextFactory();

      const nodeData = terminalNodeDataFactory();
      await createNodeContext({
        workflowContext,
        nodeData,
      });
      workflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: {
            id: "5f64210f-ec43-48ce-ae40-40a9ba4c4c11",
            key: 'Bad \\"Input\\"',
            type: "STRING",
          },
          workflowContext,
        })
      );
      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate correct code with an output variable mapped to a non-existent node", async () => {
      const workflowContext = workflowContextFactory({ strict: false });
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

      workflowContext.addOutputVariableContext(
        new OutputVariableContext({
          outputVariableData: {
            id: "output-variable-id",
            key: "passthrough",
            type: "STRING",
          },
          workflowContext,
        })
      );

      workflowContext.addWorkflowOutputContext(
        new WorkflowOutputContext({
          workflowOutputValue: {
            outputVariableId: "output-variable-id",
            value: {
              type: "NODE_OUTPUT",
              nodeId: "non-existent-node-id",
              nodeOutputId: "output-id",
            },
          },
          workflowContext,
        })
      );

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      const errors = workflowContext.getErrors();

      expect(errors.length).toEqual(1);
      expect(errors[0]?.message).toEqual(
        "Failed to find node with id 'non-existent-node-id'"
      );
      expect(errors[0]?.severity).toEqual("WARNING");
    });

    it("should generate correct code with an output variable mapped to an unused terminal node", async () => {
      const terminalNode = terminalNodeDataFactory();
      const workflowContext = workflowContextFactory({
        strict: false,
        workflowRawData: {
          nodes: [terminalNode],
          edges: [],
        },
      });
      await createNodeContext({
        workflowContext,
        nodeData: terminalNode,
      });

      workflowContext.addOutputVariableContext(
        new OutputVariableContext({
          outputVariableData: {
            id: "output-variable-id",
            key: "passthrough",
            type: "STRING",
          },
          workflowContext,
        })
      );

      workflowContext.addWorkflowOutputContext(
        new WorkflowOutputContext({
          workflowOutputValue: {
            outputVariableId: "output-variable-id",
            value: {
              type: "NODE_OUTPUT",
              nodeId: terminalNode.id,
              nodeOutputId: terminalNode.data.outputId,
            },
          },
          workflowContext,
        })
      );

      const workflow = codegen.workflow({
        workflowContext,
      });

      workflow.getWorkflowFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
