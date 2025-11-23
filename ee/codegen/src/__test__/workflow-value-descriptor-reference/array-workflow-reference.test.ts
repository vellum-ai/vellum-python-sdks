import { vi } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { WorkflowContext } from "src/context";
import { Writer } from "src/generators/extensions/writer";
import { ArrayWorkflowReference } from "src/generators/workflow-value-descriptor-reference/array-workflow-reference";
import { ArrayWorkflowReference as ArrayWorkflowReferenceType } from "src/types/vellum";

describe("ArrayWorkflowReference", () => {
  let workflowContext: WorkflowContext;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("should generate correct AST for empty array", async () => {
    const emptyArrayReference: ArrayWorkflowReferenceType = {
      type: "ARRAY_REFERENCE",
      items: [],
    };

    const reference = new ArrayWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: emptyArrayReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for array with constant values", async () => {
    const arrayReference: ArrayWorkflowReferenceType = {
      type: "ARRAY_REFERENCE",
      items: [
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "Hello, World!",
          },
        },
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "NUMBER",
            value: 42,
          },
        },
      ],
    };

    const reference = new ArrayWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: arrayReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for nested arrays", async () => {
    const nestedArrayReference: ArrayWorkflowReferenceType = {
      type: "ARRAY_REFERENCE",
      items: [
        {
          type: "ARRAY_REFERENCE",
          items: [
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "STRING",
                value: "Inner value",
              },
            },
            {
              type: "CONSTANT_VALUE",
              value: {
                type: "NUMBER",
                value: 100,
              },
            },
          ],
        },
        {
          type: "CONSTANT_VALUE",
          value: {
            type: "STRING",
            value: "Outer value",
          },
        },
      ],
    };

    const reference = new ArrayWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: nestedArrayReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate correct AST for array with expression values", async () => {
    const exprArrayReference: ArrayWorkflowReferenceType = {
      type: "ARRAY_REFERENCE",
      items: [
        {
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
        {
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
      ],
    };

    const reference = new ArrayWorkflowReference({
      workflowContext,
      nodeInputWorkflowReferencePointer: exprArrayReference,
    });

    const writer = new Writer();
    reference.write(writer);

    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
