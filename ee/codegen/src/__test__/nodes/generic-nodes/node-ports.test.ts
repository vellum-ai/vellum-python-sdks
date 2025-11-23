import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  genericNodeFactory,
  nodePortFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { GenericNodeContext } from "src/context/node-context/generic-node";
import { Writer } from "src/generators/extensions/writer";
import { NodePorts } from "src/generators/node-port";
import { NodePort } from "src/types/vellum";

describe("NodePorts", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let nodePorts: NodePorts;

  beforeEach(async () => {
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

    await createNodeContext({
      workflowContext,
      nodeData: genericNodeFactory({
        id: "node-1",
        label: "TestNode",
        nodeOutputs: [{ id: "output-1", name: "my-output", type: "STRING" }],
      }),
    });
  });

  describe("basic", () => {
    beforeEach(async () => {
      const nodePortsData: NodePort[] = [
        nodePortFactory({
          type: "IF",
        }),
        nodePortFactory({
          type: "ELSE",
        }),
      ];

      const nodeData = genericNodeFactory({
        label: "MyGenericNode",
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
        nodePortFactory({
          type: "IF",
        }),
        nodePortFactory({
          type: "ELIF",
          expression: {
            type: "BINARY_EXPRESSION",
            operator: "=",
            lhs: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "NODE_OUTPUT",
                nodeId: "node-1",
                nodeOutputId: "output-1",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "expected-value",
                },
              },
            },
            rhs: {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: "another-expected-value",
              },
            },
          },
        }),
        nodePortFactory({
          type: "ELSE",
        }),
      ];

      const nodeData = genericNodeFactory({
        label: "MyGenericNode",
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

  describe("basic duplicate port names", () => {
    beforeEach(async () => {
      // GIVEN a node with duplicate port names
      const duplicateName = "same port name";
      const nodePortsData: NodePort[] = [
        nodePortFactory({
          type: "IF",
          name: duplicateName,
          expression: {
            type: "CONSTANT_VALUE",
            value: {
              type: "STRING",
              value: "test-value-1",
            },
          },
        }),
        nodePortFactory({
          type: "ELIF",
          name: duplicateName,
          expression: {
            type: "CONSTANT_VALUE",
            value: {
              type: "STRING",
              value: "test-value-2",
            },
          },
        }),
        nodePortFactory({
          type: "ELSE",
          name: "unique_name",
        }),
      ];

      const nodeData = genericNodeFactory({
        label: "GenericNodeWithDuplicatePorts",
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

    it("handles duplicate port names correctly", async () => {
      nodePorts.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("empty expression for if port", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });
      const nodePortsData: NodePort[] = [
        {
          type: "IF",
          id: "ae4343de-fe31-4ed9-9447-0cf5c27bef7c",
          name: "my_if_port",
          expression: undefined,
        },
        nodePortFactory({
          type: "ELSE",
        }),
      ];

      const nodeData = genericNodeFactory({
        label: "MyGenericNode",
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

      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toEqual(
        "Expected IF / ELIF Ports to contain an expression"
      );
      expect(errors[0]?.severity).toBe("WARNING");
    });
  });

  describe("nested binary expression with OR operator", () => {
    beforeEach(async () => {
      const nodePortsData: NodePort[] = [
        nodePortFactory({
          type: "IF",
          expression: {
            type: "BINARY_EXPRESSION",
            operator: "or",
            lhs: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "NODE_OUTPUT",
                nodeId: "node-1",
                nodeOutputId: "output-1",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "STRING",
                  value: "first-value",
                },
              },
            },
            rhs: {
              type: "BINARY_EXPRESSION",
              operator: "=",
              lhs: {
                type: "WORKFLOW_INPUT",
                inputVariableId: "input-1",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "NUMBER",
                  value: 42,
                },
              },
            },
          },
        }),
        nodePortFactory({
          type: "ELSE",
        }),
      ];

      const nodeData = genericNodeFactory({
        label: "NestedOrOperatorNode",
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

    it("generates correct ports class with nested OR operator", async () => {
      nodePorts.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("nested binary expression with AND operator", () => {
    beforeEach(async () => {
      const nodePortsData: NodePort[] = [
        nodePortFactory({
          type: "IF",
          expression: {
            type: "BINARY_EXPRESSION",
            operator: "and",
            lhs: {
              type: "BINARY_EXPRESSION",
              operator: ">",
              lhs: {
                type: "WORKFLOW_INPUT",
                inputVariableId: "input-1",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "NUMBER",
                  value: 10,
                },
              },
            },
            rhs: {
              type: "BINARY_EXPRESSION",
              operator: "<",
              lhs: {
                type: "WORKFLOW_INPUT",
                inputVariableId: "input-1",
              },
              rhs: {
                type: "CONSTANT_VALUE",
                value: {
                  type: "NUMBER",
                  value: 100,
                },
              },
            },
          },
        }),
        nodePortFactory({
          type: "ELSE",
        }),
      ];

      const nodeData = genericNodeFactory({
        label: "NestedAndOperatorNode",
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

    it("generates correct ports class with nested AND operator", async () => {
      nodePorts.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
