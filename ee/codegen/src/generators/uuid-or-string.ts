import { python } from "@fern-api/python-ast";
import { validate as uuidValidate } from "uuid";

import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export class UuidOrString extends AstNode {
  private id: string;

  public constructor(id: string) {
    super();
    this.id = id;
  }

  generateId(id: string): python.TypeInstantiation {
    return uuidValidate(id)
      ? python.TypeInstantiation.uuid(id)
      : python.TypeInstantiation.str(id);
  }

  write(writer: Writer): void {
    this.generateId(this.id).write(writer);
  }
}
