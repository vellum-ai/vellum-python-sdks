import { Writer } from "@fern-api/python-ast/core/Writer";

import * as codegen from "src/codegen";

describe("VellumValue", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  describe("STRING", () => {
    it("should write a STRING value correctly", async () => {
      const stringValue = codegen.vellumValue({
        vellumValue: {
          type: "STRING",
          value: "Hello, World!",
        },
      });
      stringValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(stringValue.getReferences()).toHaveLength(0);
    });
  });

  describe("NUMBER", () => {
    it("should write a NUMBER value correctly", async () => {
      const numberValue = codegen.vellumValue({
        vellumValue: {
          type: "NUMBER",
          value: 42,
        },
      });
      numberValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(numberValue.getReferences()).toHaveLength(0);
    });
  });

  describe("CHAT_HISTORY", () => {
    it("should write a CHAT_HISTORY value with just text", async () => {
      const chatHistoryValue = codegen.vellumValue({
        vellumValue: {
          type: "CHAT_HISTORY",
          value: [
            {
              role: "USER",
              text: "Hello, AI!",
            },
          ],
        },
      });
      chatHistoryValue.write(writer);
      expect(writer.toString()).toMatchSnapshot();
      expect(chatHistoryValue.getReferences()).toHaveLength(1);
    });

    it("should write a CHAT_HISTORY value with a string content", async () => {
      const chatHistoryValue = codegen.vellumValue({
        vellumValue: {
          type: "CHAT_HISTORY",
          value: [
            {
              role: "USER",
              content: { type: "STRING", value: "Hello, AI!" },
            },
          ],
        },
      });
      chatHistoryValue.write(writer);
      expect(writer.toString()).toMatchSnapshot();
      expect(chatHistoryValue.getReferences()).toHaveLength(2);
    });

    it("should write nothing when CHAT_HISTORY value is null", async () => {
      const chatHistoryValue = codegen.vellumValue({
        vellumValue: {
          type: "CHAT_HISTORY",
        },
      });
      chatHistoryValue.write(writer);
      expect(writer.toString()).toMatchSnapshot();
      expect(chatHistoryValue.getReferences()).toHaveLength(0);
    });

    it("should write empty list when CHAT_HISTORY value is empty list", async () => {
      const chatHistoryValue = codegen.vellumValue({
        vellumValue: {
          type: "CHAT_HISTORY",
          value: [],
        },
      });
      chatHistoryValue.write(writer);
      expect(writer.toString()).toMatchSnapshot();
      expect(chatHistoryValue.getReferences()).toHaveLength(0);
    });
  });

  describe("JSON", () => {
    it("should write a JSON value correctly", async () => {
      const jsonValue = codegen.vellumValue({
        vellumValue: {
          type: "JSON",
          value: {
            key: "value",
            nested: { array: [1, 2, 3] },
          },
        },
      });
      jsonValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(jsonValue.getReferences()).toHaveLength(0);
    });
  });

  describe("ERROR", () => {
    it("should write a ERROR value correctly", async () => {
      const errorValue = codegen.vellumValue({
        vellumValue: {
          type: "ERROR",
          value: {
            message: "This is an error!",
            code: "INTERNAL_SERVER_ERROR",
          },
        },
      });
      errorValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(errorValue.getReferences()).toHaveLength(1);
    });
  });

  describe("IMAGE", () => {
    it("should write a IMAGE value correctly", async () => {
      const imageValue = codegen.vellumValue({
        vellumValue: {
          type: "IMAGE",
          value: {
            src: "https://example.com/image.png",
          },
        },
      });
      imageValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(imageValue.getReferences()).toHaveLength(1);
    });
  });

  describe("FUNCTION_CALL", () => {
    it("should write a FUNCTION_CALL value correctly", async () => {
      const functionCallValue = codegen.vellumValue({
        vellumValue: {
          type: "FUNCTION_CALL",
          value: {
            arguments: {
              key: "value",
            },
            name: "test",
            id: "123",
          },
        },
      });
      functionCallValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(functionCallValue.getReferences()).toHaveLength(1);
    });
  });

  describe("ARRAY", () => {
    it("should write a ARRAY value correctly", async () => {
      const arrayValue = codegen.vellumValue({
        vellumValue: {
          type: "ARRAY",
          value: [
            {
              type: "STRING",
              value: "Hello, World!",
            },
            {
              type: "NUMBER",
              value: 42,
            },
            {
              type: "AUDIO",
              value: {
                src: "https://example.com/audio.mp3",
              },
            },
          ],
        },
      });
      arrayValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(arrayValue.getReferences()).toHaveLength(1);
    });
  });

  describe("AUDIO", () => {
    it("should write a AUDIO value correctly", async () => {
      const audioValue = codegen.vellumValue({
        vellumValue: {
          type: "AUDIO",
          value: {
            src: "https://example.com/audio.mp3",
          },
        },
      });
      audioValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(audioValue.getReferences()).toHaveLength(1);
    });
  });

  describe("DOCUMENT", () => {
    it("should write a DOCUMENT value correctly", async () => {
      const documentValue = codegen.vellumValue({
        vellumValue: {
          type: "DOCUMENT",
          value: {
            src: "https://example.com/document.pdf",
          },
        },
      });
      documentValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(documentValue.getReferences()).toHaveLength(1);
    });
  });

  describe("SEARCH_RESULTS", () => {
    it("should write a SEARCH_RESULTS value correctly", async () => {
      const searchResultsValue = codegen.vellumValue({
        vellumValue: {
          type: "SEARCH_RESULTS",
          value: [
            {
              text: "Hello, World!",
              score: 0.5,
              keywords: ["hello", "world"],
              document: {
                id: "123",
                label: "Example Document",
              },
            },
            {
              text: "Hello, AI!",
              score: 0.7,
              keywords: ["hello", "ai"],
              document: {
                id: "456",
                label: "Another Document",
              },
            },
          ],
        },
      });
      searchResultsValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(searchResultsValue.getReferences()).toHaveLength(4);
    });
  });

  describe("VIDEO", () => {
    it("should write a VIDEO value correctly", async () => {
      const videoValue = codegen.vellumValue({
        vellumValue: {
          type: "VIDEO",
          value: {
            src: "https://example.com/video.mp4",
          },
        },
      });
      videoValue.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
      expect(videoValue.getReferences()).toHaveLength(1);
    });
  });
});
