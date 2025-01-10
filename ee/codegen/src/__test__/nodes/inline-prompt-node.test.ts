import { Writer } from "@fern-api/python-ast/core/Writer";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  inlinePromptNodeDataInlineVariantFactory,
  inlinePromptNodeDataLegacyVariantFactory,
} from "src/__test__/helpers/node-data-factories";
import { createNodeContext, WorkflowContext } from "src/context";
import { InlinePromptNodeContext } from "src/context/node-context/inline-prompt-node";
import { InlinePromptNode } from "src/generators/nodes/inline-prompt-node";

describe("InlinePromptNode", () => {
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
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as InlinePromptNodeContext;
        workflowContext.addNodeContext(nodeContext);

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

    describe("reject on error enabled", () => {
      beforeEach(async () => {
        const nodeData = inlinePromptNodeDataInlineVariantFactory({
          blockType,
          errorOutputId: "e7a1fbea-f5a7-4b31-a9ff-0d26c3de021f",
        });

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as InlinePromptNodeContext;
        workflowContext.addNodeContext(nodeContext);

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

    describe("legacy prompt variant", () => {
      beforeEach(async () => {
        const nodeData = inlinePromptNodeDataLegacyVariantFactory({
          blockType,
        });

        vi.spyOn(workflowContext, "getMLModelNameById").mockResolvedValue(
          "gpt-4o-mini"
        );

        const nodeContext = (await createNodeContext({
          workflowContext,
          nodeData,
        })) as InlinePromptNodeContext;
        workflowContext.addNodeContext(nodeContext);

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
  });
});
