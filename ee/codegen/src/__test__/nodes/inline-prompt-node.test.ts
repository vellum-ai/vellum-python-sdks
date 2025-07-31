import { Writer } from "@fern-api/python-ast/core/Writer";
import { v4 as uuidv4 } from "uuid";
import { PromptSettings } from "vellum-ai/api";
import { beforeEach } from "vitest";

import { workflowContextFactory } from "src/__test__/helpers";
import { inputVariableContextFactory } from "src/__test__/helpers/input-variable-context-factory";
import {
  genericNodeFactory,
  inlinePromptNodeDataInlineVariantFactory,
  inlinePromptNodeDataLegacyVariantFactory,
  nodeInputFactory,
} from "src/__test__/helpers/node-data-factories";
import { stateVariableContextFactory } from "src/__test__/helpers/state-variable-context-factory";
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
        }).build();

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
        }).build();

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
    }).build();

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
    }).build();

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
      const nodeData = inlinePromptNodeDataInlineVariantFactory({})
        .withOutputs(nodeOutputs)
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
      const nodeData = inlinePromptNodeDataInlineVariantFactory({})
        .withAttributes(nodeAttributes)
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
  });

  describe("basic with stream setting false", () => {
    let node: InlinePromptNode;
    beforeEach(async () => {
      const promptSettings: PromptSettings = {
        streamEnabled: false,
      };
      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        settings: promptSettings,
      }).build();

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

  describe("basic with undefined template", () => {
    it("should generate node file", async () => {
      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        defaultBlock: {
          blockType: "JINJA",
          properties: {
            template: "",
          },
          id: uuidv4(),
          state: "DISABLED",
        },
      }).build();

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
  });

  describe("basic with node inputs and the prompt_inputs attribute defined", () => {
    it("should generate node file prioritizing the latter", async () => {
      const workflowContext = workflowContextFactory();

      const textStateVariableId = uuidv4();
      workflowContext.addStateVariableContext(
        stateVariableContextFactory({
          stateVariableData: {
            id: textStateVariableId,
            key: "text",
            type: "STRING",
          },
          workflowContext,
        })
      );

      const nodeData = inlinePromptNodeDataInlineVariantFactory({
        inputs: [
          nodeInputFactory({
            id: uuidv4(),
            key: "foo",
            value: {
              type: "CONSTANT_VALUE",
              data: {
                type: "STRING",
                value: "bar",
              },
            },
          }),
        ],
      })
        .withAttributes([
          {
            id: uuidv4(),
            name: "prompt_inputs",
            value: {
              type: "DICTIONARY_REFERENCE",
              entries: [
                {
                  key: "text",
                  value: {
                    type: "WORKFLOW_STATE",
                    stateVariableId: textStateVariableId,
                  },
                },
              ],
            },
          },
        ])
        .build();

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
  });

  describe("basic with custom, same module, base", () => {
    it("getNodeFile", async () => {
      workflowContext = workflowContextFactory({
        moduleName: "my.custom.path",
      });

      const nodeData = inlinePromptNodeDataInlineVariantFactory({ inputs: [] })
        .withBase({
          name: "MyInlinePrompt",
          module: ["my", "custom", "path", "nodes", "my_inline_prompt"],
        })
        .build();

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
  });

  describe("with functions attribute", () => {
    it("should generate functions field with WorkflowValueDescriptor for upstream node output", async () => {
      await createNodeContext({
        workflowContext,
        nodeData: genericNodeFactory({
          id: "upstream-node-id",
          label: "FunctionsProviderNode",
          nodeOutputs: [
            { id: "functions-output-id", name: "functions", type: "JSON" },
          ],
        }),
      });

      const functionsAttribute: NodeAttributeType = {
        id: uuidv4(),
        name: "functions",
        value: {
          type: "NODE_OUTPUT",
          nodeId: "upstream-node-id",
          nodeOutputId: "functions-output-id",
        },
      };

      const nodeData = inlinePromptNodeDataInlineVariantFactory({})
        .withAttributes([functionsAttribute])
        .build();

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
  });

  describe("with node trigger AWAIT_ALL", () => {
    it("should generate Trigger class with AWAIT_ALL", async () => {
      const nodeData = inlinePromptNodeDataInlineVariantFactory({})
        .withTrigger({
          id: uuidv4(),
          mergeBehavior: "AWAIT_ALL",
        })
        .build();

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
  });

  describe("with node trigger AWAIT_ANY", () => {
    it("should generate Trigger class with AWAIT_ANY", async () => {
      const nodeData = inlinePromptNodeDataInlineVariantFactory({})
        .withTrigger({
          id: uuidv4(),
          mergeBehavior: "AWAIT_ANY",
        })
        .build();

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
  });

  describe("LEGACY prompt node API failure handling", () => {
    it("should handle getMLModelNameById API failure gracefully", async () => {
      const legacyNodeData = inlinePromptNodeDataLegacyVariantFactory({
        blockType: "JINJA",
      });

      workflowContext.getMLModelNameById = vi
        .fn()
        .mockRejectedValue(new Error("API call failed: ML model not found"));

      const nodeContext = new InlinePromptNodeContext({
        workflowContext,
        nodeData: legacyNodeData as unknown as InlinePromptNode,
      });

      await expect(nodeContext.buildProperties()).rejects.toThrow(
        "Failed to convert LEGACY prompt node to INLINE"
      );
      await expect(nodeContext.buildProperties()).rejects.toThrow(
        /ML model name/
      );
    });
  });
});
