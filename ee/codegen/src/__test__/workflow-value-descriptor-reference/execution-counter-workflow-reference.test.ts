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
import { ExecutionCounterWorkflowReference } from "src/generators/workflow-value-descriptor-reference/execution-counter-workflow-reference";
import {
  WorkflowDataNode,
  WorkflowValueDescriptorReference,
} from "src/types/vellum";

describe("ExecutionCounterWorkflowReferencePointer", () => {
  let workflowContext: WorkflowContext;
  let node: WorkflowDataNode;

  beforeEach(async () => {
    workflowContext = workflowContextFactory();
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );
    node = searchNodeDataFactory().build();
    await nodeContextFactory({ workflowContext, nodeData: node });
  });

  it("should generate correct AST for execution counter reference", async () => {
    const counterReference: WorkflowValueDescriptorReference = {
      type: "EXECUTION_COUNTER",
      nodeId: node.id,
    };

    const pointer = new ExecutionCounterWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: counterReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
  it("should generate Lazy Reference for self-referencing nodes", async () => {
    const counterReference: WorkflowValueDescriptorReference = {
      type: "EXECUTION_COUNTER",
      nodeId: node.id,
    };

    const pointer = new ExecutionCounterWorkflowReference({
      nodeContext: workflowContext.findNodeContext(node.id),
      workflowContext,
      nodeInputWorkflowReferencePointer: counterReference,
    });

    const writer = new Writer();
    pointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
