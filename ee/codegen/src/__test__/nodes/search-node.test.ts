import { Writer } from "@fern-api/python-ast/core/Writer";
import { VellumError } from "vellum-ai";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { afterEach, beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { searchNodeDataFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { TextSearchNodeContext } from "src/context/node-context/text-search-node";
import { SearchNode } from "src/generators/nodes/search-node";

describe("TextSearchNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: SearchNode;

  beforeEach(() => {
    vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockResolvedValue(
      mockDocumentIndexFactory() as unknown as DocumentIndexRead
    );

    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "a6ef8809-346e-469c-beed-2e5c4e9844c5",
          key: "query",
          type: "STRING",
        },
        workflowContext,
      })
    );

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "c95cccdc-8881-4528-bc63-97d9df6e1d87",
          key: "var1",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });
  afterEach(async () => {
    vi.restoreAllMocks();
  });
  describe("basic", () => {
    beforeEach(async () => {
      const nodeData = searchNodeDataFactory();

      const nodeContext = createNodeContext({
        workflowContext,
        nodeData,
      }) as TextSearchNodeContext;
      workflowContext.addNodeContext(nodeContext);
      await nodeContext.buildProperties();

      node = new SearchNode({
        workflowContext: workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("reject on error enabled", () => {
    beforeEach(async () => {
      const nodeData = searchNodeDataFactory({
        errorOutputId: "af589f73-effe-4a80-b48f-fb912ac6ce67",
      });

      const nodeContext = createNodeContext({
        workflowContext,
        nodeData,
      }) as TextSearchNodeContext;
      workflowContext.addNodeContext(nodeContext);
      await nodeContext.buildProperties();

      node = new SearchNode({
        workflowContext: workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("metadata filters", () => {
    beforeEach(async () => {
      const nodeData = searchNodeDataFactory({
        metadataFiltersNodeInputId: "371f2f88-d125-4c49-9775-01aa86df2767",
        metadataFilterInputs: [
          {
            id: "500ce391-ee26-4588-a5a0-2dfa6b70add5",
            key: "vellum-query-builder-variable-500ce391-ee26-4588-a5a0-2dfa6b70add5",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "TYPE",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "3321686c-b131-4651-a18c-3e578252abf4",
            key: "vellum-query-builder-variable-500ce391-ee26-4588-a5a0-2dfa6b70add5",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "VENDOR",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "28682e34-ef0c-47fd-a32e-8228a53360b0",
            key: "vellum-query-builder-variable-28682e34-ef0c-47fd-a32e-8228a53360b0",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "STATUS",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "65a90810-f26b-4848-9c7f-29f324450e07",
            key: "vellum-query-builder-variable-28682e34-ef0c-47fd-a32e-8228a53360b0",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "1",
                  },
                },
              ],
              combinator: "OR",
            },
          },
          {
            id: "4f88fdee-4bee-40d8-a998-bbbc7255029c",
            key: "vellum-query-builder-variable-4f88fdee-4bee-40d8-a998-bbbc7255029c",
            value: {
              rules: [
                {
                  type: "CONSTANT_VALUE",
                  data: {
                    type: "STRING",
                    value: "DELETED_AT",
                  },
                },
              ],
              combinator: "OR",
            },
          },
        ],
        metadataFilters: {
          type: "LOGICAL_CONDITION_GROUP",
          negated: false,
          combinator: "AND",
          conditions: [
            {
              type: "LOGICAL_CONDITION",
              operator: "=",
              lhsVariableId: "500ce391-ee26-4588-a5a0-2dfa6b70add5",
              rhsVariableId: "3321686c-b131-4651-a18c-3e578252abf4",
            },
            {
              type: "LOGICAL_CONDITION",
              operator: "=",
              lhsVariableId: "28682e34-ef0c-47fd-a32e-8228a53360b0",
              rhsVariableId: "65a90810-f26b-4848-9c7f-29f324450e07",
            },
            {
              type: "LOGICAL_CONDITION",
              operator: "null",
              lhsVariableId: "4f88fdee-4bee-40d8-a998-bbbc7255029c",
              rhsVariableId: "dc1b9237-5fde-4d9f-9648-792475e02cfa",
            },
          ],
        },
      });

      const nodeContext = createNodeContext({
        workflowContext,
        nodeData,
      }) as TextSearchNodeContext;
      workflowContext.addNodeContext(nodeContext);
      await nodeContext.buildProperties();

      node = new SearchNode({
        workflowContext: workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("getNodeDisplayFile", async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("404 error handling", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });

      vi.spyOn(DocumentIndexesClient.prototype, "retrieve").mockImplementation(
        () => {
          throw new VellumError({ message: "test", statusCode: 404, body: {} });
        }
      );

      const nodeData = searchNodeDataFactory();

      const nodeContext = createNodeContext({
        workflowContext,
        nodeData,
      }) as TextSearchNodeContext;
      workflowContext.addNodeContext(nodeContext);
      await nodeContext.buildProperties();

      node = new SearchNode({
        workflowContext: workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile handles 404 error", async () => {
      node.getNodeFile().write(writer);
      await writer.toStringFormatted();

      expect(workflowContext.getErrors()[0]?.message).toEqual(
        'Document Index "d5beca61-aacb-4b22-a70c-776a1e025aa4" not found.'
      );
    });
  });
});
