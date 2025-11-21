import * as python from "@fern-api/python-ast";
import { Writer } from "@fern-api/python-ast/core/Writer";

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
    expect(writer.toString()).toBe("Union[float, int]");
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

  it("should convert array schema with string items to List[str] type", () => {
    const schema = {
      type: "array",
      items: {
        type: "string",
      },
    };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("List[str]");
  });

  it("should convert array schema without items to List[Any] type", () => {
    const schema = { type: "array" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("List[Any]");
  });

  it("should convert object schema to Dict[str, Any] type", () => {
    const schema = { type: "object" };
    const result = jsonSchemaToType(schema);
    result.write(writer);
    expect(writer.toString()).toBe("Dict[str, Any]");
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
    expect(writer.toString()).toBe("List[List[int]]");
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
});
