import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { genericNodeFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { NodePorts } from "src/generators/node-port";
import { NodePort, WorkflowDataNode } from "src/types/vellum";

describe("NodePorts", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let nodePorts: NodePorts;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-1",
          key: "count",
          type: "NUMBER",
        },
        workflowContext,
      })
    );

    vi.spyOn(workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortsData: NodePort[] = [
        {
          type: "IF",
          id: "port-2",
          name: "if_port",
          expression: {
            type: "UNARY_EXPRESSION",
            operator: "null",
            lhs: {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "input-1",
              },
            },
          },
        },
        {
          type: "ELSE",
          id: "port-3",
          name: "else_port",
        },
      ];

      const nodeData = genericNodeFactory({
        name: "MyGenericNode",
        nodePorts: nodePortsData,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      nodePorts = new NodePorts({
        nodePorts: nodePortsData,
        nodeContext,
        workflowContext,
      });
    });

    it("generates correct ports class", async () => {
      nodePorts.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("basic with nested expression in port", () => {
    beforeEach(async () => {
      const nodePortsData: NodePort[] = [
        {
          type: "IF",
          id: "port-2",
          name: "if_port",
          expression: {
            type: "UNARY_EXPRESSION",
            operator: "null",
            lhs: {
              type: "INPUT_VARIABLE",
              data: {
                inputVariableId: "input-1",
              },
            },
          },
        },
        {
          type: "ELIF",
          id: "port-2",
          name: "elif_port",
          expression: {
            type: "BINARY_EXPRESSION",
            operator: "=",
            lhs: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "NODE_OUTPUT",
                data: {
                  nodeId: "node-1",
                  outputId: "output-1",
                },
              },
              rhs: {
                type: "CONSTANT_VALUE",
                data: {
                  type: "STRING",
                  value: "expected-value",
                },
              },
            },
            rhs: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "another-expected-value",
              },
            },
          },
        },
        {
          type: "ELSE",
          id: "port-3",
          name: "else_port",
        },
      ];

      const nodeData = genericNodeFactory({
        name: "MyGenericNode",
        nodePorts: nodePortsData,
      });

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as GenericNodeContext;

      nodePorts = new NodePorts({
        nodePorts: nodePortsData,
        nodeContext,
        workflowContext,
      });
    });

    it("generates correct ports class", async () => {
      nodePorts.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
