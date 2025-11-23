import { workflowContextFactory } from "./helpers";

import { WorkflowContext } from "src/context/workflow-context";
import { Writer } from "src/generators/extensions/writer";
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

  describe("IMAGE", () => {
    it("should generate a basic image block", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "IMAGE",
          state: "ENABLED",
          src: "https://example.com/image.png",
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("IMAGE with metadata", () => {
    it("should generate an image block with metadata", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "IMAGE",
          state: "ENABLED",
          src: "https://example.com/image.png",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("CHAT_MESSAGE with file input block", () => {
    it("should generate a chat message block with static file input blocks", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "CHAT_MESSAGE",
          state: "ENABLED",
          properties: {
            chatRole: "USER",
            chatMessageUnterminated: false,
            blocks: [
              {
                id: "2",
                blockType: "IMAGE",
                state: "ENABLED",
                src: "https://example.com/image.png",
              },
            ],
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("AUDIO", () => {
    it("should generate a basic audio block", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "AUDIO",
          state: "ENABLED",
          src: "https://example.com/audio.mp3",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("VIDEO", () => {
    it("should generate a basic video block", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "VIDEO",
          state: "ENABLED",
          src: "https://example.com/video.mp4",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("DOCUMENT", () => {
    it("should generate a basic document block", async () => {
      const block = new StatefulPromptBlock({
        workflowContext,
        promptBlock: {
          id: "1",
          blockType: "DOCUMENT",
          state: "ENABLED",
          src: "https://example.com/document.pdf",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
        inputVariableNameById: {},
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
