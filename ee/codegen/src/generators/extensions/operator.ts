export { OperatorType } from "@fern-api/python-ast/OperatorType";
import { OperatorType } from "@fern-api/python-ast/OperatorType";

import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export declare namespace Operator {
  interface Args {
    operator: OperatorType;
    lhs: AstNode;
    rhs: AstNode;
  }
}

export class Operator extends AstNode {
  private readonly operator: OperatorType;
  private readonly lhs: AstNode;
  private readonly rhs: AstNode;

  constructor({ operator, lhs, rhs }: Operator.Args) {
    super();
    this.operator = operator;
    this.lhs = lhs;
    this.inheritReferences(lhs);
    this.rhs = rhs;
    this.inheritReferences(rhs);
  }

  private getOperatorString(): string {
    switch (this.operator) {
      case "or":
        return "or";
      case "and":
        return "and";
      case "add":
        return "+";
      case "subtract":
        return "-";
      case "multiple":
        return "*";
      case "divide":
        return "/";
      case "modulo":
        return "%";
      case "leftShift":
        return "<<";
      case "rightShift":
        return ">>";
      default: {
        const _exhaustiveCheck: never = this.operator;
        throw new Error(`Unknown operator: ${_exhaustiveCheck}`);
      }
    }
  }

  write(writer: Writer): void {
    this.lhs.write(writer);
    writer.write(" ");
    writer.write(this.getOperatorString());
    writer.write(" ");
    this.rhs.write(writer);
  }
}
