import { Writer } from "@fern-api/python-ast/core/Writer";
import { VellumError } from "vellum-ai";
import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { afterEach, beforeEach, vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { mockDocumentIndexFactory } from "src/__test__/helpers/document-index-factory";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  nodeInputFactory,
  searchNodeDataFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { TextSearchNodeContext } from "src/context/node-context/text-search-node";
import {
  NodeAttributeGenerationError,
  ValueGenerationError,
} from "src/generators/errors";
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
      const nodeData = searchNodeDataFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
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
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
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
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
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

  describe("limit param should cast string to int", () => {
    beforeEach(async () => {
      const nodeData = searchNodeDataFactory({
        limitInput: {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "8",
          },
        },
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("limit param should throw exception if casting string that is not an int", () => {
    beforeEach(async () => {
      const nodeData = searchNodeDataFactory({
        limitInput: {
          type: "CONSTANT_VALUE",
          data: {
            type: "STRING",
            value: "not-a-number",
          },
        },
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
    });

    it("should throw ValueGenerationError", async () => {
      await expect(async () => {
        node.getNodeFile().write(writer);
        await writer.toStringFormatted();
      }).rejects.toThrow(
        new ValueGenerationError(
          'Failed to parse search node limit value "not-a-number" as an integer'
        )
      );
    });
  });

  describe("limit param should throw exception if not a constant value of type number", () => {
    beforeEach(async () => {
      const nodeData = searchNodeDataFactory({
        limitInput: {
          type: "CONSTANT_VALUE",
          data: {
            type: "JSON",
            value: "{}",
          },
        },
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
    });

    it("should throw NodeAttributeGenerationError", async () => {
      await expect(async () => {
        node.getNodeFile().write(writer);
        await writer.toStringFormatted();
      }).rejects.toThrow(
        new NodeAttributeGenerationError(
          "Limit param input should be a CONSTANT_VALUE and of type NUMBER, got JSON instead"
        )
      );
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

      const nodeData = searchNodeDataFactory().build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
    });

    it("getNodeFile handles 404 error", async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();

      const error = workflowContext.getErrors()[0];
      expect(error).toBeDefined();
      expect(error?.message).toEqual(
        'Document Index "d5beca61-aacb-4b22-a70c-776a1e025aa4" not found.'
      );
      expect(error?.severity).toEqual("WARNING");
    });
  });

  describe("should codegen successfully without document index id input", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });

      const nodeData = searchNodeDataFactory({
        includeDocumentIndexInput: false,
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
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

  describe("should codegen successfully without metadata filters mapped properly", () => {
    it("LHS missing on getNodeDisplayClassBodyStatements", async () => {
      const workflowContext = workflowContextFactory({ strict: false });

      const nodeData = searchNodeDataFactory({
        metadataFilters: {
          type: "LOGICAL_CONDITION_GROUP",
          conditions: [
            {
              type: "LOGICAL_CONDITION",
              operator: "=",
              lhsVariableId: "9263f669-dfb4-4d69-820d-15beca7583b3",
              rhsVariableId: "8a3b603a-5c73-47f6-a2e5-88f3de7bd847",
            },
          ],
          combinator: "AND",
          negated: false,
        },
        metadataFilterInputs: [
          nodeInputFactory({
            id: "1237381c-2e78-4306-bd62-be8ecc900d02",
            key: "filters.metadata.conditions.0.lhs",
            value: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "field",
              },
            },
          }),
          nodeInputFactory({
            id: "3c56555f-45dc-43d5-9d1c-b7cecf70cea1",
            key: "filters.metadata.conditions.0.rhs",
            value: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "foo",
              },
            },
          }),
        ],
        queryInput: nodeInputFactory({
          id: "2f5bc81d-6ee8-4101-9a55-4ddeae954425",
          key: "query",
          value: {
            type: "CONSTANT_VALUE",
            data: { type: "STRING", value: "find me documents" },
          },
        }),
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();

      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toBe(
        "Could not find search node query input for the left hand side of condition 0"
      );
      expect(errors[0]?.severity).toEqual("WARNING");
    });

    it("RHS missing on getNodeDisplayClassBodyStatements", async () => {
      const workflowContext = workflowContextFactory({ strict: false });

      const lhsVariableId = "9263f669-dfb4-4d69-820d-15beca7583b3";
      const nodeData = searchNodeDataFactory({
        metadataFilters: {
          type: "LOGICAL_CONDITION_GROUP",
          conditions: [
            {
              type: "LOGICAL_CONDITION",
              operator: "=",
              lhsVariableId,
              rhsVariableId: "8a3b603a-5c73-47f6-a2e5-88f3de7bd847",
            },
          ],
          combinator: "AND",
          negated: false,
        },
        metadataFilterInputs: [
          nodeInputFactory({
            id: lhsVariableId,
            key: "filters.metadata.conditions.0.lhs",
            value: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "field",
              },
            },
          }),
          nodeInputFactory({
            id: "3c56555f-45dc-43d5-9d1c-b7cecf70cea1",
            key: "filters.metadata.conditions.0.rhs",
            value: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "foo",
              },
            },
          }),
        ],
        queryInput: nodeInputFactory({
          id: "2f5bc81d-6ee8-4101-9a55-4ddeae954425",
          key: "query",
          value: {
            type: "CONSTANT_VALUE",
            data: { type: "STRING", value: "find me documents" },
          },
        }),
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();

      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toBe(
        "Could not find search node query input for the right hand side of condition 0"
      );
      expect(errors[0]?.severity).toEqual("WARNING");
    });
  });

  describe("null weights", () => {
    beforeEach(async () => {
      workflowContext = workflowContextFactory({ strict: false });
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

      const nodeData = searchNodeDataFactory({
        weightsInput: {
          type: "CONSTANT_VALUE",
          data: { type: "JSON", value: null },
        },
      }).build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as TextSearchNodeContext;

      node = new SearchNode({
        workflowContext,
        nodeContext,
      });
    });

    it("adds a warning to workflow context", async () => {
      node.getNodeFile().write(writer);
      await writer.toStringFormatted();
      const errors = workflowContext.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0]?.message).toBe(
        "weights input is null; defaulting to None"
      );
      expect(errors[0]?.severity).toEqual("WARNING");
    });
  });
});
