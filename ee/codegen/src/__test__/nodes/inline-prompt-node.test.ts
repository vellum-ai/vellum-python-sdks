import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";
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
import {
  NodeAttribute as NodeAttributeType,
  NodeOutput as NodeOutputType,
  PromptTemplateBlock,
} from "src/types/vellum";

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

  it("should generate prompt parameters correctly", async () => {
    const nodeData = inlinePromptNodeDataInlineVariantFactory({
      parameters: {
        temperature: 0.12,
        maxTokens: 345,
        topP: 0.67,
        topK: 8,
        frequencyPenalty: 0.9,
        presencePenalty: 0.11,
        stop: ["foo", "bar"],
        logitBias: {
          foo: 0.1,
          bar: 0.2,
        },
        customParameters: {
          foo: "bar",
        },
      },
    });

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as InlinePromptNodeContext;

    const node = new InlinePromptNode({
      workflowContext,
      nodeContext,
    });
    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it("should generate cache config correctly", async () => {
    const block: PromptTemplateBlock = {
      id: "1",
      blockType: "JINJA",
      state: "ENABLED",
      properties: {
        template: "Hello, {{ name }}!",
      },
      cacheConfig: {
        type: "EPHEMERAL",
      },
    };

    const nodeData = inlinePromptNodeDataInlineVariantFactory({
      blockType: "JINJA",
      defaultBlock: block,
    });

    const nodeContext = (await createNodeContext({
      workflowContext,
      nodeData,
    })) as InlinePromptNodeContext;

    const node = new InlinePromptNode({
      workflowContext,
      nodeContext,
    });

    node.getNodeFile().write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  describe("with json output id defined", async () => {
    let node: InlinePromptNode;
    beforeEach(async () => {
      const randomJsonOutputId = "some-json-output-id";
      const nodeOutputs: NodeOutputType[] = [
        {
          id: randomJsonOutputId,
          name: "json",
          type: "JSON",
        },
      ];
      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        outputs: nodeOutputs,
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

    it(`getNodeDisplayFile`, async () => {
      node.getNodeDisplayFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("with ml model node attribute defined", async () => {
    let node: InlinePromptNode;
    beforeEach(async () => {
      const randomMlModelAttrId = uuidv4();
      const nodeAttributes: NodeAttributeType[] = [
        {
          id: randomMlModelAttrId,
          name: "ml_model",
          value: {
            type: "CONSTANT_VALUE",
            value: {
              type: "STRING",
              value: "gpt-4",
            },
          },
        },
      ];
      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        attributes: nodeAttributes,
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

    it(`getNodeFile`, async () => {
      node.getNodeFile().write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
