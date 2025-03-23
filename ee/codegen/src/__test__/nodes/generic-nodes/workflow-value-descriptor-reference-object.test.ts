import { Writer } from "@fern-api/python-ast/core/Writer";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { vi } from "vitest";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { searchNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { WorkflowValueDescriptorReferenceObject } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference-object";
import {
  WorkflowDataNode,
  WorkflowValueDescriptor as WorkflowValueDescriptorType,
} from "src/types/vellum";

describe("WorkflowValueDescriptorReferenceObject", () => {
  let writer: Writer;
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    writer = new Writer();
    workflowContext = workflowContextFactory();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct AST for CONSTANT_VALUE reference", async () => {
    const constantValueDescriptor: WorkflowValueDescriptorType = {
      type: "CONSTANT_VALUE",
      value: {
        type: "STRING",
        value: "Hello, World!",
      },
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: constantValueDescriptor,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for NODE_OUTPUT reference", async () => {
    vi.spyOn(workflowContext, "findNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeOutputDescriptor: WorkflowValueDescriptorType = {
      type: "NODE_OUTPUT",
      nodeId: "test-node-id",
      nodeOutputId: "test-output-id",
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: nodeOutputDescriptor,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for VELLUM_SECRET reference", async () => {
    const secretDescriptor: WorkflowValueDescriptorType = {
      type: "VELLUM_SECRET",
      vellumSecretName: "API_KEY",
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: secretDescriptor,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for EXECUTION_COUNTER reference", async () => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );
    const node = searchNodeDataFactory();
    await nodeContextFactory({ workflowContext, nodeData: node });
    const counterDescriptor: WorkflowValueDescriptorType = {
      type: "EXECUTION_COUNTER",
      nodeId: node.id,
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: counterDescriptor,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for WORKFLOW_INPUT reference", async () => {
    const inputDescriptor: WorkflowValueDescriptorType = {
      type: "WORKFLOW_INPUT",
      inputVariableId: "test-input-id",
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: inputDescriptor,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for WORKFLOW_STATE reference", async () => {
    const stateDescriptor: WorkflowValueDescriptorType = {
      type: "WORKFLOW_STATE",
      stateVariableId: "test-state-id",
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: stateDescriptor,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for UNARY_EXPRESSION", async () => {
    const unaryExpression: WorkflowValueDescriptorType = {
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

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: unaryExpression,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for BINARY_EXPRESSION", async () => {
    const binaryExpression: WorkflowValueDescriptorType = {
      type: "BINARY_EXPRESSION",
      operator: "=",
      lhs: {
        type: "CONSTANT_VALUE",
        value: {
          type: "STRING",
          value: "Hello",
        },
      },
      rhs: {
        type: "CONSTANT_VALUE",
        value: {
          type: "STRING",
          value: "World",
        },
      },
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: binaryExpression,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for TERNARY_EXPRESSION", async () => {
    const ternaryExpression: WorkflowValueDescriptorType = {
      type: "TERNARY_EXPRESSION",
      operator: "between",
      base: {
        type: "CONSTANT_VALUE",
        value: {
          type: "NUMBER",
          value: 5,
        },
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

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: ternaryExpression,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for nested BINARY_EXPRESSION with 4 node outputs", async () => {
    vi.spyOn(workflowContext, "findNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    // Create a nested binary expression with 4 node outputs
    const nestedBinaryExpression: WorkflowValueDescriptorType = {
      type: "BINARY_EXPRESSION",
      operator: "coalesce",
      lhs: {
        type: "BINARY_EXPRESSION",
        operator: "coalesce",
        lhs: {
          type: "BINARY_EXPRESSION",
          operator: "coalesce",
          lhs: {
            type: "NODE_OUTPUT",
            nodeId: "node-id-1",
            nodeOutputId: "output-id-1",
          },
          rhs: {
            type: "NODE_OUTPUT",
            nodeId: "node-id-2",
            nodeOutputId: "output-id-2",
          },
        },
        rhs: {
          type: "NODE_OUTPUT",
          nodeId: "node-id-3",
          nodeOutputId: "output-id-3",
        },
      },
      rhs: {
        type: "NODE_OUTPUT",
        nodeId: "node-id-4",
        nodeOutputId: "output-id-4",
      },
    };

    const referenceObject = new WorkflowValueDescriptorReferenceObject({
      workflowContext,
      workflowValueDescriptor: nestedBinaryExpression,
    });

    referenceObject.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
