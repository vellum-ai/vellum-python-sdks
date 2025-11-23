import { v4 as uuidv4 } from "uuid";
import { beforeEach, describe, expect, it } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import { inlinePromptNodeDataInlineVariantFactory } from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { Writer } from "src/generators/extensions/writer";
import { InlinePromptNode } from "src/generators/nodes/inline-prompt-node";
import { AdornmentNode } from "src/types/vellum";

describe("InlinePromptRetryNode", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;
  let node: InlinePromptNode;

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

  describe("basic", () => {
    beforeEach(async () => {
      const adornmentData: AdornmentNode[] = [
        {
          id: "cc79c784-d936-44c2-a811-b86a53e6ff68",
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
      ];
      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
      })
        .withAdornments(adornmentData)
        .build();

      const nodeContext = (await createNodeContext({
        workflowContext,
        nodeData,
      })) as InlinePromptNodeContext;

      node = new InlinePromptNode({
        workflowContext,
        nodeContext,
      });
    });

    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it(`getNodeDisplayFile`, async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
  describe("basic retry adornment with delay", () => {
    let node: InlinePromptNode;

    beforeEach(async () => {
      const adornmentData: AdornmentNode[] = [
        {
          id: "2076aea8-be38-4ff1-8c68-cb853e352d66",
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
      ];
      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
      })
        .withAdornments(adornmentData)
        .build();

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
      const adornmentData: AdornmentNode[] = [
        {
          id: "e5de8d57-ae0d-4a4a-afb3-eb4cd6bdb0ac",
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
      ];

      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        blockType: "JINJA",
        errorOutputId: ERROR_OUTPUT_ID,
      })
        .withAdornments(adornmentData)
        .build();

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
