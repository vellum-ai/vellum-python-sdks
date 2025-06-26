import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import {
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";

describe("WorkflowValueDescriptor", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

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

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "input-2",
          key: "another_count",
          type: "NUMBER",
        },
        workflowContext,
      })
    );

    vi.spyOn(workflowContext, "findNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);
  });

  describe("expressions", () => {
    it("generates unary expression with input variable", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "UNARY_EXPRESSION",
        operator: "null",
        lhs: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-1",
        },
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("generates unary expression with constant value for parse_json", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "UNARY_EXPRESSION",
        operator: "parseJson",
        lhs: {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: '{"key": "value"}',
          },
        },
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("generates binary expression with node output and constant", async () => {
      const descriptor: WorkflowValueDescriptorType = {
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
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("generates binary expression with nested workflow value descriptors", async () => {
      const descriptor: WorkflowValueDescriptorType = {
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
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("generates ternary expression with input variables", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "TERNARY_EXPRESSION",
        operator: "between",
        base: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-1",
        },
        lhs: {
          type: "CONSTANT_VALUE",
          value: {
            type: "NUMBER",
            value: 1,
          },
        },
        rhs: {
          type: "CONSTANT_VALUE",
          value: {
            type: "NUMBER",
            value: 10,
          },
        },
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("generates unary expression with is_error operator", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "UNARY_EXPRESSION",
        operator: "isError",
        lhs: {
          type: "NODE_OUTPUT",
          nodeId: "node-1",
          nodeOutputId: "output-1",
        },
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("expressions that begin with constant values", () => {
    it("generates unary expression beginning with constant value reference", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "UNARY_EXPRESSION",
        operator: "null",
        lhs: {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "Hello, World!",
          },
        },
      };

      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("generates binary expression beginning with constant value reference", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "BINARY_EXPRESSION",
        operator: "=",
        lhs: {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "Hello, World!",
          },
        },
        rhs: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-1",
        },
      };
      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("generates ternary expression beginning with constant value reference", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "TERNARY_EXPRESSION",
        operator: "between",
        base: {
          type: "CONSTANT_VALUE",
          value: {
            type: "NUMBER",
            value: 123,
          },
        },
        lhs: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-1",
        },
        rhs: {
          type: "WORKFLOW_INPUT",
          inputVariableId: "input-2",
        },
      };
      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("generates unary expression with is_error operator on constant value", async () => {
      const descriptor: WorkflowValueDescriptorType = {
        type: "UNARY_EXPRESSION",
        operator: "isError",
        lhs: {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "Some error message",
          },
        },
      };
      const valueDescriptor = new WorkflowValueDescriptor({
        workflowValueDescriptor: descriptor,
        workflowContext,
      });

      valueDescriptor.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
