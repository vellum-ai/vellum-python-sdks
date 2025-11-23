import { vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";
import { DictionaryWorkflowReference } from "src/generators/workflow-value-descriptor-reference/dictionary-workflow-reference";
import { DictionaryWorkflowReference as DictionaryWorkflowReferenceType } from "src/types/vellum";

describe("DictionaryWorkflowReference", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should allow null value", async () => {
    const emptyDictReference: DictionaryWorkflowReferenceType = {
      type: "DICTIONARY_REFERENCE",
      entries: [{ key: "text", value: null }],
    };

    const reference = new DictionaryWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: emptyDictReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for empty dictionary", async () => {
    const emptyDictReference: DictionaryWorkflowReferenceType = {
      type: "DICTIONARY_REFERENCE",
      entries: [],
    };

    const reference = new DictionaryWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: emptyDictReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for dictionary with constant values", async () => {
    const dictReference: DictionaryWorkflowReferenceType = {
      type: "DICTIONARY_REFERENCE",
      entries: [
        {
          key: "string_value",
          value: {
            type: "CONSTANT_VALUE",
            value: {
              type: "STRING",
              value: "Hello, World!",
            },
          },
        },
        {
          key: "number_value",
          value: {
            type: "CONSTANT_VALUE",
            value: {
              type: "NUMBER",
              value: 42,
            },
          },
        },
      ],
    };

    const reference = new DictionaryWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: dictReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for nested dictionaries", async () => {
    const nestedDictReference: DictionaryWorkflowReferenceType = {
      type: "DICTIONARY_REFERENCE",
      entries: [
        {
          key: "nested_dict",
          value: {
            type: "DICTIONARY_REFERENCE",
            entries: [
              {
                key: "inner_key",
                value: {
                  type: "CONSTANT_VALUE",
                  value: {
                    type: "STRING",
                    value: "Inner value",
                  },
                },
              },
              {
                key: "another_inner_key",
                value: {
                  type: "CONSTANT_VALUE",
                  value: {
                    type: "NUMBER",
                    value: 100,
                  },
                },
              },
            ],
          },
        },
        {
          key: "outer_key",
          value: {
            type: "CONSTANT_VALUE",
            value: {
              type: "STRING",
              value: "Outer value",
            },
          },
        },
      ],
    };

    const reference = new DictionaryWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: nestedDictReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for dictionary with expression values", async () => {
    const exprDictReference: DictionaryWorkflowReferenceType = {
      type: "DICTIONARY_REFERENCE",
      entries: [
        {
          key: "unary_expression",
          value: {
            type: "UNARY_EXPRESSION",
            operator: "null",
            lhs: {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: "check if null",
              },
            },
          },
        },
        {
          key: "binary_expression",
          value: {
            type: "BINARY_EXPRESSION",
            operator: "=",
            lhs: {
              type: "CONSTANT_VALUE",
              value: {
                type: "NUMBER",
                value: 10,
              },
            },
            rhs: {
              type: "CONSTANT_VALUE",
              value: {
                type: "NUMBER",
                value: 10,
              },
            },
          },
        },
      ],
    };

    const reference = new DictionaryWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: exprDictReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
  it("should generate correct AST for dictionary with definition", async () => {
    const definitionDictReference: DictionaryWorkflowReferenceType = {
      type: "DICTIONARY_REFERENCE",
      entries: [
        {
          id: "160c6ef1-30b4-40ff-8cad-88d73bc6ea54",
          key: "chat_history",
          value: {
            type: "BINARY_EXPRESSION",
            lhs: {
              type: "WORKFLOW_STATE",
              stateVariableId: "2ae688ad-8690-4765-a5fa-aecc7d6496e5",
            },
            operator: "+",
            rhs: {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  id: "f50f80a5-3b36-4077-a90f-c13b38fd7919",
                  key: "text",
                  value: {
                    type: "WORKFLOW_INPUT",
                    inputVariableId: "cb4bd466-58e9-4ecd-a2b3-22ce280a0422",
                  },
                },
                {
                  id: "2047e859-8c1a-42b9-b4d4-b6d6fc7b33b2",
                  key: "role",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "STRING", value: "USER" },
                  },
                },
                {
                  id: "ca0c0a31-e903-4908-998d-10916e287d77",
                  key: "content",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "JSON", value: null },
                  },
                },
                {
                  id: "78565b95-23a0-4be4-a9ce-89893a60f458",
                  key: "source",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: { type: "JSON", value: null },
                  },
                },
              ],
              definition: {
                name: "ChatMessage",
                module: ["vellum", "client", "types", "chat_message"],
              },
            },
          },
        },
      ],
    };

    workflowContext.addStateVariableContext(
      stateVariableContextFactory({
        stateVariableData: {
          id: "2ae688ad-8690-4765-a5fa-aecc7d6496e5",
          key: "chat_history",
          type: "CHAT_HISTORY",
        },
        workflowContext,
      })
    );

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "cb4bd466-58e9-4ecd-a2b3-22ce280a0422",
          key: "text",
          type: "STRING",
        },
        workflowContext,
      })
    );

    const reference = new DictionaryWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: definitionDictReference,
    });
    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
