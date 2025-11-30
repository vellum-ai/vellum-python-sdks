import { Reference } from "./reference";
import { PythonType } from "./type";

import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export class UnionType extends PythonType {
  private readonly itemTypes: AstNode[];

  constructor(itemTypes: AstNode[]) {
    super();
    this.itemTypes = itemTypes;
    this.addReference(new Reference({ name: "Union", modulePath: ["typing"] }));
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
