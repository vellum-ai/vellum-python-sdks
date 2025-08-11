import { Writer } from "@fern-api/python-ast/core/Writer";

import { workflowContextFactory } from "./helpers";

import { WorkflowContext } from "src/context/workflow-context";
import { StatefulPromptBlock } from "src/generators/stateful-prompt-block";

describe("StatefulPromptBlock", () => {
  let workflowContext: WorkflowContext;
  let writer: Writer;

  beforeEach(() => {
    workflowContext = workflowContextFactory();
    writer = new Writer();
  });

  describe("JINJA", () => {
    it("should generate a basic jinja block", async () => {
      const block = new StatefulPromptBlock({
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
      const block = new StatefulPromptBlock({
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
      const block = new StatefulPromptBlock({
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

  describe("PLAIN_TEXT", () => {
    it("should generate regular quotes for empty text", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "PLAIN_TEXT",
          state: "ENABLED",
          text: "",
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
