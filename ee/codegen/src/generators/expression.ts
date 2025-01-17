import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { NodeAttributeGenerationError } from "src/generators/errors";

export declare namespace Expression {
  interface Args {
    lhs: AstNode;
    expression: string;
    rhs?: AstNode | undefined;
    base?: AstNode | undefined;
  }
}

export class Expression extends AstNode {
  private readonly astNode: AstNode;

  constructor({ lhs, expression, rhs, base }: Expression.Args) {
    super();
    this.astNode = this.generateAstNode({ lhs, expression, rhs, base });
  }

  private generateAstNode({
    lhs,
    expression,
    rhs,
    base,
  }: Expression.Args): AstNode {
    this.inheritReferences(lhs);
    if (rhs) {
      this.inheritReferences(rhs);
    }

    // TODO: We should ideally perform this using native fern functionality, but it requires being able to create
    //  a Reference object from an existing AstNode, which in turn requires all AstNode's to internally track their
    //  name and modulePath.

    const rawExpression = base
      ? this.generateExpressionWithBase(base, expression, lhs, rhs)
      : this.generateStandardExpression(lhs, expression, rhs);

    return python.codeBlock(rawExpression);
  }

  private generateExpressionWithBase(
    base: AstNode,
    expression: string,
    lhs: AstNode,
    rhs: AstNode | undefined
  ): string {
    if (!rhs) {
      throw new NodeAttributeGenerationError(
        "rhs must be defined if base is defined"
      );
    }
    this.inheritReferences(base);
    return `${base.toString()}.${expression}(${lhs.toString()}, ${rhs.toString()})`;
  }

  private generateStandardExpression(
    lhs: AstNode,
    expression: string,
    rhs: AstNode | undefined
  ): string {
    const rhsExpression = rhs ? `(${rhs.toString()})` : "()";
    return `${lhs.toString()}.${expression}${rhsExpression}`;
  }

  public write(writer: Writer) {
    this.astNode.write(writer);
  }
}
