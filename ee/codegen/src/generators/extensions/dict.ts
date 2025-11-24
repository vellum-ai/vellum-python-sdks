import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { PythonType } from "./type";

import { Writer } from "src/generators/extensions/writer";

/**
 * Creates a built-in dict type annotation using lowercase `dict[K, V]` instead of `Dict[K, V]` from typing.
 * This is the modern Python 3.9+ syntax that doesn't require importing from typing.
 */
export class BuiltinDictType extends PythonType {
  private readonly keyType: AstNode;
  private readonly valueType: AstNode;

  constructor(keyType: AstNode, valueType: AstNode) {
    super();
    this.keyType = keyType;
    this.valueType = valueType;
    this.inheritReferences(keyType);
    this.inheritReferences(valueType);
  }

  write(writer: Writer): void {
    writer.write("dict[");
    this.keyType.write(writer);
    writer.write(", ");
    this.valueType.write(writer);
    writer.write("]");
  }
}
