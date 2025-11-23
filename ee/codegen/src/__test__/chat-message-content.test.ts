import { ChatMessageContent } from "src/generators/chat-message-content";
import { Writer } from "src/generators/extensions/writer";

describe("ChatMessageContent", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  describe("STRING", () => {
    it("should write a string content correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: { type: "STRING", value: "Hello, AI!" },
      });
      chatMessageContent.write(writer);
      expect(writer.toString()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(1);
    });

    it("should write a string with nested quotes correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "STRING",
          value:
            '{"tool_calls":[{"id":"call_123","type":"function","function":{"name":"generate_query","arguments":"{\\"query\\":\\"SELECT * FROM users WHERE id = 1\\"}"}}]}',
        },
      });
      chatMessageContent.write(writer);
      expect(writer.toString()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(1);
    });
  });

  describe("FUNCTION_CALL", () => {
    it("should write a function call content with id correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "FUNCTION_CALL",
          value: {
            id: "123",
            name: "get_weather",
            arguments: {
              location: "New York",
              unit: "celsius",
            },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });

    it("should write a function call content without id correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "FUNCTION_CALL",
          value: {
            name: "get_weather",
            arguments: {
              location: "New York",
              unit: "celsius",
            },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });

    it("should write a function call content with id as null correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "FUNCTION_CALL",
          value: {
            id: null as unknown as string,
            name: "get_weather",
            arguments: {
              location: "New York",
              unit: "celsius",
            },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });
  });
  describe("ARRAY", () => {
    it("should write an array of content correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "ARRAY",
          value: [
            {
              type: "STRING",
              value: "First message",
            },
            {
              type: "FUNCTION_CALL",
              value: {
                name: "get_weather",
                arguments: {
                  location: "Seattle",
                },
              },
            },
          ],
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(4);
    });
  });

  describe("AUDIO", () => {
    it("should write an audio content correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "AUDIO",
          value: {
            src: "https://example.com/audio.mp3",
            metadata: { key: "value" },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });
  });

  describe("IMAGE", () => {
    it("should write an image content correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "IMAGE",
          value: {
            src: "https://example.com/image.png",
            metadata: { key: "value" },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });
  });

  describe("DOCUMENT", () => {
    it("should write a document content correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "DOCUMENT",
          value: {
            src: "https://example.com/document.pdf",
            metadata: { key: "value" },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });
  });

  describe("VIDEO", () => {
    it("should write a video content correctly", async () => {
      const chatMessageContent = new ChatMessageContent({
        chatMessageContent: {
          type: "VIDEO",
          value: {
            src: "https://example.com/video.mp4",
            metadata: { key: "value" },
          },
        },
      });
      chatMessageContent.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(chatMessageContent.getReferences()).toHaveLength(2);
    });
  });
});
