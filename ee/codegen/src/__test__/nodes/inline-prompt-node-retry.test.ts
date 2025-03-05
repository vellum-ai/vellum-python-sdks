import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { inlinePromptNodeDataInlineVariantFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { InlinePromptNode } from "src/generators/nodes/inline-prompt-node";

describe("InlinePromptRetryNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();

    workflowContext.addInputVariableContext(
      inputVariableContextFactory({
        inputVariableData: {
          id: "90c6afd3-06cc-430d-aed1-35937c062531",
          key: "text",
          type: "STRING",
        },
        workflowContext,
      })
    );
  });

  const promptInputBlockTypes = [
    "JINJA",
    "CHAT_MESSAGE",
    "FUNCTION_DEFINITION",
    "VARIABLE",
    "RICH_TEXT",
  ] as const;

  describe.each(promptInputBlockTypes)("%s block type", (blockType) => {
    let node: InlinePromptNode;

    describe("basic", () => {
      beforeEach(async () => {
        const nodeData = inlinePromptNodeDataInlineVariantFactory({
          blockType,
          adornments: [
            {
              id: uuidv4(),
              label: "RetryNodeLabel",
              base: {
                name: "RetryNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "core",
                  "retry_node",
                  "node",
                ],
              },
              attributes: [
                {
                  id: uuidv4(),
                  name: "max_attempts",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "NUMBER",
                      value: 3,
                    },
                  },
                },
              ],
            },
          ],
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as InlinePromptNodeContext;

        node = new InlinePromptNode({
          workflowContext,
          nodeContext,
        });
      });

      it(`getNodeFile for ${blockType} block type`, async () => {
        node.getNodeFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });
      it(`getNodeDisplayFile for ${blockType} block type`, async () => {
        node.getNodeDisplayFile().write(writer);
        expect(await writer.toStringFormatted()).toMatchSnapshot();
      });
    });
    describe("basic retry adornment with delay", () => {
      let node: InlinePromptNode;

      beforeEach(async () => {
        const nodeData = inlinePromptNodeDataInlineVariantFactory({
          blockType: blockType,
          adornments: [
            {
              id: uuidv4(),
              label: "RetryNodeLabel",
              base: {
                name: "RetryNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "core",
                  "retry_node",
                  "node",
                ],
              },
              attributes: [
                {
                  id: uuidv4(),
                  name: "max_attempts",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "NUMBER",
                      value: 3,
                    },
                  },
                },
                {
                  id: uuidv4(),
                  name: "delay",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "NUMBER",
                      value: 2,
                    },
                  },
                },
              ],
            },
          ],
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as InlinePromptNodeContext;

        node = new InlinePromptNode({
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

    describe("basic retry adornment and try adornment", () => {
      let node: InlinePromptNode;
      const ERROR_OUTPUT_ID = "e7a1fbea-f5a7-4b31-a9ff-0d26c3de021f";

      beforeEach(async () => {
        // Create a prompt node with both errorOutputId and retry adornment
        const nodeData = inlinePromptNodeDataInlineVariantFactory({
          blockType: blockType,
          errorOutputId: ERROR_OUTPUT_ID,
          adornments: [
            {
              id: uuidv4(),
              label: "RetryNodeLabel",
              base: {
                name: "RetryNode",
                module: [
                  "vellum",
                  "workflows",
                  "nodes",
                  "core",
                  "retry_node",
                  "node",
                ],
              },
              attributes: [
                {
                  id: uuidv4(),
                  name: "max_attempts",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "NUMBER",
                      value: 3,
                    },
                  },
                },
                {
                  id: uuidv4(),
                  name: "delay",
                  value: {
                    type: "CONSTANT_VALUE",
                    value: {
                      type: "NUMBER",
                      value: 2,
                    },
                  },
                },
              ],
            },
          ],
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as InlinePromptNodeContext;

        node = new InlinePromptNode({
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
  });
});
