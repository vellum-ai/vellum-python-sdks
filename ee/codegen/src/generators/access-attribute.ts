import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

export declare namespace AccessAttribute {
  interface Args {
    lhs: AstNode;
    rhs: AstNode;
  }
}

export class AccessAttribute extends AstNode {
  private readonly lhs: AstNode;
  private readonly rhs: AstNode;

  constructor({ lhs, rhs }: AccessAttribute.Args) {
    super();

    this.lhs = lhs;
    this.inheritReferences(lhs);

    this.rhs = rhs;
    this.inheritReferences(rhs);
  }

  public write(writer: Writer): void {
    this.lhs.write(writer);
    writer.write(".");
    this.rhs.write(writer);
  }
}
