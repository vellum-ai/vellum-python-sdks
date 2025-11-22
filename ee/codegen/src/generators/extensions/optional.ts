import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { PythonType } from "./type";

/**
 * Creates a built-in list type annotation using lowercase `list[T]` instead of `List[T]` from typing.
 * This is the modern Python 3.9+ syntax that doesn't require importing from typing.
 */
export class OptionalType extends PythonType {
  private readonly itemType: AstNode;

  constructor(itemType: AstNode) {
    super();
    this.itemType = itemType;
    this.addReference(
      python.reference({ name: "Optional", modulePath: ["typing"] })
    );
    this.inheritReferences(itemType);
  }

  write(writer: Writer): void {
    writer.write("Optional[");
    this.itemType.write(writer);
    writer.write("]");
  }
}
