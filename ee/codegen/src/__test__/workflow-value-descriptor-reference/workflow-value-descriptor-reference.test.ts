import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { vi } from "vitest";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { searchNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
import { WorkflowValueDescriptorReference } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference";
import {
  WorkflowDataNode,
  WorkflowValueDescriptorReference as WorkflowValueDescriptorReferenceType,
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
    const constantValueReference: WorkflowValueDescriptorReferenceType = {
      type: "CONSTANT_VALUE",
      value: {
        type: "STRING",
        value: "Hello, World!",
      },
    };

    const reference = new WorkflowValueDescriptorReference({
      workflowContext,
      workflowValueReferencePointer: constantValueReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for NODE_OUTPUT reference", async () => {
    vi.spyOn(workflowContext, "findNodeContext").mockReturnValue({
      nodeClassName: "TestNode",
      path: ["nodes", "test-node-path"],
      getNodeOutputNameById: vi.fn().mockReturnValue("my_output"),
    } as unknown as BaseNodeContext<WorkflowDataNode>);

    const nodeOutputReference: WorkflowValueDescriptorReferenceType = {
      type: "NODE_OUTPUT",
      nodeId: "test-node-id",
      nodeOutputId: "test-output-id",
    };

    const reference = new WorkflowValueDescriptorReference({
      workflowContext,
      workflowValueReferencePointer: nodeOutputReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for VELLUM_SECRET reference", async () => {
    const secretReference: WorkflowValueDescriptorReferenceType = {
      type: "VELLUM_SECRET",
      vellumSecretName: "API_KEY",
    };

    const reference = new WorkflowValueDescriptorReference({
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
    const node = searchNodeDataFactory().build();
    await nodeContextFactory({ workflowContext, nodeData: node });
    const counterReference: WorkflowValueDescriptorReferenceType = {
      type: "EXECUTION_COUNTER",
      nodeId: node.id,
    };

    const reference = new WorkflowValueDescriptorReference({
      workflowContext,
      workflowValueReferencePointer: counterReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for WORKFLOW_STATE reference", async () => {
    const workflowContext = workflowContextFactory({ strict: false });
    workflowContext.addStateVariableContext(
      stateVariableContextFactory({
        workflowContext,
        stateVariableData: {
          id: "someStateVariableId",
          key: "some_key",
          type: "STRING",
        },
      })
    );

    const stateReference: WorkflowValueDescriptorReferenceType = {
      type: "WORKFLOW_STATE",
      stateVariableId: "someStateVariableId",
    };

    const reference = new WorkflowValueDescriptorReference({
      workflowContext,
      workflowValueReferencePointer: stateReference,
    });

    reference.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
