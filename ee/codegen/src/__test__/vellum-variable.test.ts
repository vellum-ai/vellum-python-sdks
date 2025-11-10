import { Writer } from "@fern-api/python-ast/core/Writer";

import * as codegen from "src/codegen";

describe("VellumVariableField", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  test("StringVellumVariable snapshot", async () => {
    const stringVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "STRING", required: true },
    });
    stringVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("NumberVellumVariable snapshot", async () => {
    const numberVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "NUMBER", required: true },
    });
    numberVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("JsonVellumVariable snapshot", async () => {
    const jsonVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "JSON", required: true },
    });
    jsonVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("AudioVellumVariable snapshot", async () => {
    const audioVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "AUDIO", required: true },
    });
    audioVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("VideoVellumVariable snapshot", async () => {
    const videoVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "VIDEO", required: true },
    });
    videoVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("ImageVellumVariable snapshot", async () => {
    const imageVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "IMAGE", required: true },
    });
    imageVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("DocumentVellumVariable snapshot", async () => {
    const documentVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "DOCUMENT", required: true },
    });
    documentVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("FunctionCallVellumVariable snapshot", async () => {
    const functionCallVar = codegen.vellumVariable({
      variable: {
        id: "1",
        name: "test",
        type: "FUNCTION_CALL",
        required: true,
      },
    });
    functionCallVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("ErrorVellumVariable snapshot", async () => {
    const errorVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "ERROR", required: true },
    });
    errorVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("ArrayVellumVariable snapshot", async () => {
    const arrayVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "ARRAY", required: true },
    });
    arrayVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("ChatHistoryVellumVariable snapshot", async () => {
    const chatHistoryVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "CHAT_HISTORY", required: true },
    });
    chatHistoryVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("SearchResultsVellumVariable snapshot", async () => {
    const searchResultsVar = codegen.vellumVariable({
      variable: {
        id: "1",
        name: "test",
        type: "SEARCH_RESULTS",
        required: true,
      },
    });
    searchResultsVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("NullVellumVariable snapshot", async () => {
    const nullVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "NULL" },
    });
    nullVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("OptionalVellumVariable defaultRequired=true snapshot", async () => {
    const optionalVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "STRING" },
      defaultRequired: true,
    });
    optionalVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  test("OptionalVellumVariable defaultRequired=false snapshot", async () => {
    const optionalVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "STRING" },
      defaultRequired: false,
    });
    optionalVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });

  it.each([true, false])(
    "ArrayVellumVariable with empty list default uses Field(default_factory=list) when %s",
    async (required: boolean) => {
      const arrayVar = codegen.vellumVariable({
        variable: {
          id: "1",
          name: "test",
          type: "ARRAY",
          required: required,
          default: { type: "ARRAY", value: [] },
        },
      });
      arrayVar.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }
  );

  it.each([true, false])(
    "JsonVellumVariable with empty dict default uses Field(default_factory=dict) when %s",
    async (required: boolean) => {
      const jsonVar = codegen.vellumVariable({
        variable: {
          id: "1",
          name: "test",
          type: "JSON",
          required: required,
          default: { type: "JSON", value: {} },
        },
      });
      jsonVar.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }
  );

  it.each([true, false])(
    "ArrayVellumVariable with non-empty list default uses Field(default_factory=lambda: [...]) when %s",
    async (required: boolean) => {
      const arrayVar = codegen.vellumVariable({
        variable: {
          id: "1",
          name: "test",
          type: "ARRAY",
          required: required,
          default: {
            type: "ARRAY",
            value: [
              { type: "STRING", value: "item1" },
              { type: "STRING", value: "item2" },
            ],
          },
        },
      });
      arrayVar.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }
  );

  it.each([true, false])(
    "JsonVellumVariable with non-empty dict default uses Field(default_factory=lambda: {...}) when %s",
    async (required: boolean) => {
      const jsonVar = codegen.vellumVariable({
        variable: {
          id: "1",
          name: "test",
          type: "JSON",
          required: required,
          default: {
            type: "JSON",
            value: { key1: "value1", key2: "value2" },
          },
        },
      });
      jsonVar.write(writer);
      expect(await writer.toStringFormatted()).toMatchSnapshot();
    }
  );

  test("ThinkingVellumVariable snapshot", async () => {
    const thinkingVar = codegen.vellumVariable({
      variable: { id: "1", name: "test", type: "THINKING", required: true },
    });
    thinkingVar.write(writer);
    expect(await writer.toStringFormatted()).toMatchSnapshot();
  });
});
