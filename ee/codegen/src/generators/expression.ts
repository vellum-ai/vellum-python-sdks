import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

export declare namespace Expression {
  interface Args {
    lhs: AstNode;
    expression: string;
    rhs?: AstNode | undefined;
  }
}

export class Expression extends AstNode {
  private readonly astNode: AstNode;

  constructor({ lhs, expression, rhs }: Expression.Args) {
    super();

    this.astNode = this.generateAstNode({ lhs, expression, rhs });
  }

  private generateAstNode({ lhs, expression, rhs }: Expression.Args): AstNode {
    this.inheritReferences(lhs);
    if (rhs) {
      this.inheritReferences(rhs);
    }

    // TODO: We should ideally perform this using native fern functionality, but it requires being able to create
    //  a Reference object from an existing AstNode, which in turn requires all AstNode's to internally track their
    //  name and modulePath.
    const rhsExpression = rhs ? `(${rhs.toString()})` : "()";
    const rawExpression = `${lhs.toString()}.${expression}${rhsExpression}`;

    return python.codeBlock(rawExpression);
  }

  public write(writer: Writer) {
    this.astNode.write(writer);
  }
}
