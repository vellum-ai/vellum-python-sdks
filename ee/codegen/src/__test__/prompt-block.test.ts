import { workflowContextFactory } from "./helpers";

import { WorkflowContext } from "src/context/workflow-context";
import { Writer } from "src/generators/extensions/writer";
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
          blockType: "JINJA",
          template: "Hello, {{ name }}!",
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should generate a jinja block with a cache config", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "JINJA",
          template: "Hello, {{ name }}!",
          cacheConfig: {
            type: "EPHEMERAL",
          },
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });

    it("should handle double quotes in jinja template", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "JINJA",
          template: '"Hello" "World"',
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("IMAGE", () => {
    it("should generate a basic image block", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "IMAGE",
          src: "https://example.com/image.png",
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("IMAGE with metadata", () => {
    it("should generate an image block with metadata", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "IMAGE",
          src: "https://example.com/image.png",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("CHAT_MESSAGE with file input block", () => {
    it("should generate a chat message block with static file input blocks", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "CHAT_MESSAGE",
          chatRole: "USER",
          blocks: [
            {
              blockType: "IMAGE",
              src: "https://example.com/image.png",
            },
          ],
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("AUDIO", () => {
    it("should generate a basic audio block", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "AUDIO",
          src: "https://example.com/audio.mp3",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("VIDEO", () => {
    it("should generate a basic video block", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "VIDEO",
          src: "https://example.com/video.mp4",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });

  describe("DOCUMENT", () => {
    it("should generate a basic document block", async () => {
      const block = new PromptBlock({
        workflowContext,
        promptBlock: {
          blockType: "DOCUMENT",
          src: "https://example.com/document.pdf",
          metadata: {
            key: "value",
            detail: "high",
          },
        },
      });

      block.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    });
  });
});
