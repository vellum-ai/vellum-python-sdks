import { Writer } from "@fern-api/python-ast/core/Writer";
import { describe, expect, it } from "vitest";

import { python } from "src/generators/extensions/python-utils";

describe("python.class_", () => {
  it("should properly escape quotes in docs at the beginning", () => {
    const classWithStartQuote = python.class_({
      name: "TestClass",
      docs: '"Hello World',
    });

    const writer = new Writer();
    classWithStartQuote.write(writer);
    const result = writer.toString();

    expect(result).toContain('\\"Hello World');
  });

  it("should properly escape quotes in docs at the end", () => {
    const classWithEndQuote = python.class_({
      name: "TestClass",
      docs: 'Hello World"',
    });

    const writer = new Writer();
    classWithEndQuote.write(writer);
    const result = writer.toString();

    expect(result).toContain('Hello World\\"');
  });

  it("should not escape quotes in docs in the middle", () => {
    const classWithMiddleQuote = python.class_({
      name: "TestClass",
      docs: 'Hello "World',
    });

    const writer = new Writer();
    classWithMiddleQuote.write(writer);
    const result = writer.toString();

    expect(result).toContain('Hello "World');
  });
});
