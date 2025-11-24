import { PythonType } from "./type";

import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

/**
 * Creates a built-in list type annotation using lowercase `list[T]` instead of `List[T]` from typing.
 * This is the modern Python 3.9+ syntax that doesn't require importing from typing.
 */
export class BuiltinListType extends PythonType {
  private readonly itemType: AstNode;

  constructor(itemType: AstNode) {
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
