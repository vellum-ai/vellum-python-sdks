import { Writer } from "@fern-api/python-ast/core/Writer";
import { describe, expect, it } from "vitest";

import { CustomComment } from "src/generators/extensions/custom-comment";

describe("CustomComment", () => {
  it("should escape end quotes in triple-quoted strings", () => {
    const writer = new Writer();
    const comment = new CustomComment({ docs: 'Hello World"' });
    comment.write(writer);
    expect(writer.toString()).toBe('"""Hello World\\""""');
  });

  it("should escape start quotes in triple-quoted strings", () => {
    const writer = new Writer();
    const comment = new CustomComment({ docs: '"Hello World' });
    comment.write(writer);
    expect(writer.toString()).toBe('"""\\"Hello World"""');
  });

  it("should escape all double quotes in the string", () => {
    const writer = new Writer();
    const comment = new CustomComment({ docs: '"Hello "World"' });
    comment.write(writer);
    expect(writer.toString()).toBe('"""\\"Hello "World\\""""');
  });
});
