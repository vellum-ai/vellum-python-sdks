import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

export declare namespace PipeExpression {
  export interface Args {
    lhs: AstNode;
    rhs: AstNode;
  }
}

export class PipeExpression extends AstNode {
  private lhs: AstNode;
  private rhs: AstNode;

  constructor(args: PipeExpression.Args) {
    super();
    this.lhs = args.lhs;
    this.rhs = args.rhs;
    this.inheritReferences(args.lhs);
    this.inheritReferences(args.rhs);
  }

  write(writer: Writer): void {
    this.lhs.write(writer);
    writer.write(" | ");
    this.rhs.write(writer);
  }
}

export declare namespace AmpersandExpression {
  export interface Args {
    lhs: AstNode;
    rhs: AstNode;
  }
}

export class AmpersandExpression extends AstNode {
  private lhs: AstNode;
  private rhs: AstNode;

  constructor(args: AmpersandExpression.Args) {
    super();
    this.lhs = args.lhs;
    this.rhs = args.rhs;
    this.inheritReferences(args.lhs);
    this.inheritReferences(args.rhs);
  }

  write(writer: Writer): void {
    this.lhs.write(writer);
    writer.write(" & ");
    this.rhs.write(writer);
  }
}
