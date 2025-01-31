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
import { WorkflowValueDescriptorReferencePointer } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference-pointer";
import {
  WorkflowDataNode,
  WorkflowValueDescriptorReference,
} from "src/types/vellum";

describe("WorkflowValueDescriptorReferencePointer", () => {
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
    const constantValueReference: WorkflowValueDescriptorReference = {
      type: "CONSTANT_VALUE",
      value: {
        type: "STRING",
        value: "Hello, World!",
      },
    };

    const reference = new WorkflowValueDescriptorReferencePointer({
      workflowContext,
      workflowValueReferencePointer: constantValueReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for NODE_OUTPUT reference", async () => {
    vi.spyOn(workflowContext, "getNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeOutputReference: WorkflowValueDescriptorReference = {
      type: "NODE_OUTPUT",
      nodeId: "test-node-id",
      nodeOutputId: "test-output-id",
    };

    const reference = new WorkflowValueDescriptorReferencePointer({
      workflowContext,
      workflowValueReferencePointer: nodeOutputReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for VELLUM_SECRET reference", async () => {
    const secretReference: WorkflowValueDescriptorReference = {
      type: "VELLUM_SECRET",
      vellumSecretName: "API_KEY",
    };

    const reference = new WorkflowValueDescriptorReferencePointer({
      workflowContext,
      workflowValueReferencePointer: secretReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for EXECUTION_COUNTER reference", async () => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );
    const node = searchNodeDataFactory();
    await nodeContextFactory({ workflowContext, nodeData: node });
    const counterReference: WorkflowValueDescriptorReference = {
      type: "EXECUTION_COUNTER",
      nodeId: node.id,
    };

    const reference = new WorkflowValueDescriptorReferencePointer({
      workflowContext,
      workflowValueReferencePointer: counterReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should handle WORKFLOW_STATE reference with error", async () => {
    workflowContext = workflowContextFactory({ strict: false });
    const stateReference: WorkflowValueDescriptorReference = {
      type: "WORKFLOW_STATE",
      stateVariableId: "someStateVariableId",
    };

    const reference = new WorkflowValueDescriptorReferencePointer({
      workflowContext,
      workflowValueReferencePointer: stateReference,
    });

    reference.write(writer);
    const errors = workflowContext.getErrors();
    expect(errors).toHaveLength(1);
    expect(errors[0]?.message).toContain(
      `WORKFLOW_STATE reference pointers is not implemented`
    );
  });
});
