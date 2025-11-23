import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { vi } from "vitest";

import {
  nodeContextFactory,
  workflowContextFactory,
} from "src/__test__/helpers";
import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { searchNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { Writer } from "src/generators/extensions/writer";
import { ExecutionCounterPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/execution-counter-pointer";

describe("ExecutionCounterPointer", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct Python code", async () => {
    const workflowContext = workflowContextFactory();

    const node = searchNodeDataFactory().build();
    const nodeContext = await nodeContextFactory({
      workflowContext,
      nodeData: node,
    });

    const executionCounterPointer = new ExecutionCounterPointerRule({
      nodeContext,
      nodeInputValuePointerRule: {
        type: "EXECUTION_COUNTER",
        data: {
          nodeId: node.id,
        },
      },
    });

    executionCounterPointer.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
