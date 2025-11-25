import { Writer } from "src/generators/extensions/writer";
import { jsonSchemaToType } from "src/utils/vellum-variables";

describe("jsonSchemaToType", () => {
  let writer: Writer;

  beforeEach(() => {
    writer = new Writer();
  });

  it("should convert string schema to str type", () => {
    const schema = { type: "string" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("str");
  });

  it("should convert integer schema to int type", () => {
    const schema = { type: "integer" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("int");
  });

  it("should convert number schema to Union[float, int] type", () => {
    const schema = { type: "number" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("float");
  });

  it("should convert boolean schema to bool type", () => {
    const schema = { type: "boolean" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("bool");
  });

  it("should convert null schema to None type", () => {
    const schema = { type: "null" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("None");
  });

  it("should convert array schema with string items to list[str] type", () => {
    const schema = {
      type: "array",
      items: {
        type: "string",
      },
    };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("list[str]");
  });

  it("should convert array schema without items to list[Any] type", () => {
    const schema = { type: "array" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("list[Any]");
  });

  it("should convert object schema to dict[str, Any] type", () => {
    const schema = { type: "object" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("dict[str, Any]");
  });

  it("should handle nested array schemas", () => {
    const schema = {
      type: "array",
      items: {
        type: "array",
        items: {
          type: "integer",
        },
      },
    };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("list[list[int]]");
  });

  it("should return Any for unsupported schema types", () => {
    const schema = { type: "unknown" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("Any");
  });

  it("should return Any for schema without type field", () => {
    const schema = {};
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("Any");
  });

  it("should convert anyOf schema to Union[T1, T2, ...] type", () => {
    const schema = { anyOf: [{ type: "string" }, { type: "integer" }] };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("Union[str, int]");
  });

  it("should convert array schema with $ref items to list[TypeName] type", () => {
    const schema = {
      type: "array",
      items: {
        $ref: "#/$defs/vellum.client.types.chat_message.ChatMessage",
      },
    };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("list[ChatMessage]");
  });

  it("should convert top-level $ref schema to referenced type", () => {
    const schema = {
      $ref: "#/$defs/vellum.client.types.chat_message.ChatMessage",
    };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("ChatMessage");
  });
});
