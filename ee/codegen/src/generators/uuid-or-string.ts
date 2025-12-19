import { validate as uuidValidate } from "uuid";

import { AstNode } from "src/generators/extensions/ast-node";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
import { UuidInstantiation } from "src/generators/extensions/uuid-instantiation";
import { Writer } from "src/generators/extensions/writer";

export class UuidOrString extends AstNode {
  private id: string;

  public constructor(id: string) {
    super();
    this.id = id;
  }

  generateId(id: string): AstNode {
    return uuidValidate(id)
      ? new UuidInstantiation(id)
      : new StrInstantiation(id);
  }

  write(writer: Writer): void {
    this.generateId(this.id).write(writer);
  }
}
