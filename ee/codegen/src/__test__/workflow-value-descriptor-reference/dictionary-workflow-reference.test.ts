import { Writer } from "@fern-api/python-ast/core/Writer";
import { vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
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
});
