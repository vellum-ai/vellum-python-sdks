import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { PythonType } from "./type";

export class UnionType extends PythonType {
  private readonly itemTypes: AstNode[];

  constructor(itemTypes: AstNode[]) {
    super();
    this.itemTypes = itemTypes;
    this.addReference(
      python.reference({ name: "Union", modulePath: ["typing"] })
    );
    itemTypes.forEach((itemType) => this.inheritReferences(itemType));
  }

  write(writer: Writer): void {
    writer.write("Union[");
    this.itemTypes.forEach((itemType, index) => {
      if (index > 0) {
        writer.write(", ");
      }
      itemType.write(writer);
    });
    writer.write("]");
  }
}
