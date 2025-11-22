import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

/**
 * Creates a built-in list type annotation using lowercase `list[T]` instead of `List[T]` from typing.
 * This is the modern Python 3.9+ syntax that doesn't require importing from typing.
 */
export class BuiltinListType extends AstNode {
  private readonly itemType: python.Type;

  constructor(itemType: python.Type) {
    super();
    this.itemType = itemType;
    this.inheritReferences(itemType);
  }

  write(writer: Writer): void {
    writer.write("list[");
    this.itemType.write(writer);
    writer.write("]");
  }
}

export const builtinListType = (itemType: python.Type): python.Type =>
  new BuiltinListType(itemType) as unknown as python.Type;
