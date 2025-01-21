import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodeOutputs } from "src/generators/node-outputs";
import {
  NodeOutput as NodeOutputType,
  WorkflowDataNode,
} from "src/types/vellum";

describe("NodeOutput", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let nodeOutput: NodeOutputs;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodeOutputData: NodeOutputType[] = [
        {
          id: "8c3c9aff-e1d5-49f4-af75-3ec2fcbb4af2",
          name: "output",
          type: "NUMBER",
        },
      ];
      const nodeData = genericNodeFactory({
        name: "AnnotatedOutputGenericNode",
        nodeOutputs: nodeOutputData,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      workflowContext.addNodeContext(nodeContext);

      nodeOutput = new NodeOutputs({
        nodeOutputs: nodeOutputData,
        nodeContext,
        workflowContext,
      });
    });

    it("generates output class with number type", async () => {
      nodeOutput.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("workflow input output", () => {
    beforeEach(async () => {
      const nodeOutputData: NodeOutputType[] = [
        {
          id: "2c4a85c0-b017-4cea-a261-e8e8498570c9",
          name: "output",
          type: "STRING",
          value: {
            type: "INPUT_VARIABLE",
            data: {
              inputVariableId: "some-id",
            },
          },
        },
      ];
      const nodeData = genericNodeFactory({
        name: "WorkflowInputGenericNode",
        nodeOutputs: nodeOutputData,
      });

      workflowContext.addInputVariableContext(
        inputVariableContextFactory({
          inputVariableData: {
            id: "some-id",
            key: "count",
            type: "NUMBER",
          },
          workflowContext,
        })
      );

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      workflowContext.addNodeContext(nodeContext);

      nodeOutput = new NodeOutputs({
        nodeOutputs: nodeOutputData,
        nodeContext,
        workflowContext,
      });
    });

    it("generates correct output class with workflow input reference", async () => {
      nodeOutput.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("node output reference", () => {
    beforeEach(async () => {
      vi.spyOn(workflowContext, "getNodeContext").mockReturnValue({
        nodeClassName: "TestNode",
        path: ["nodes", "test-node-path"],
        getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
      } as unknown as BaseNodeContext<WorkflowDataNode>);
      const nodeOutputData: NodeOutputType[] = [
        {
          id: "db010db3-7076-4df9-ae1b-069caa16fa20",
          name: "output",
          type: "STRING",
          value: {
            type: "NODE_OUTPUT",
            data: {
              nodeId: "some-node-id",
              outputId: "some-output-id",
            },
          },
        },
      ];

      const nodeData = genericNodeFactory({
        name: "GenericNodeReferencingOutput",
        nodeOutputs: nodeOutputData,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;
      workflowContext.addNodeContext(nodeContext);

      nodeOutput = new NodeOutputs({
        nodeOutputs: nodeOutputData,
        nodeContext,
        workflowContext,
      });
    });

    it("generates correct output class with node output reference", async () => {
      nodeOutput.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
