import { workflowContextFactory } from "./helpers";

import { WorkflowContext } from "src/context/workflow-context";
import { Writer } from "src/generators/extensions";
import { PromptBlock } from "src/generators/prompt-block";

describe("PromptBlock", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("JINJA", () => {
    it("should generate a basic jinja block", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "JINJA",
          state: "ENABLED",
          properties: {
            template: "Hello, {{ name }}!",
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate a jinja block with a cache config", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "JINJA",
          state: "ENABLED",
          properties: {
            template: "Hello, {{ name }}!",
          },
          cacheConfig: {
            type: "EPHEMERAL",
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
    it("should handle double quotes in jinja template", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "JINJA",
          state: "ENABLED",
          properties: {
            template: '"Hello" "World"',
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
