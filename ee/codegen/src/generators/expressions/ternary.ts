import { WorkflowContext } from "src/context";
import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";

export declare namespace TernaryExpression {
  interface Args {
    base: AstNode;
    lhs: AstNode;
    rhs: AstNode;
    operator: string;
    workflowContext: WorkflowContext;
  }
}

export class TernaryExpression extends AstNode {
  private readonly base: AstNode;
  private readonly lhs: AstNode;
  private readonly rhs: AstNode;
  private readonly operator: string;
  private readonly workflowContext: WorkflowContext;

  constructor({
    base,
    lhs,
    rhs,
    operator,
    workflowContext,
  }: TernaryExpression.Args) {
    super();
    this.base = base;
    this.lhs = lhs;
    this.rhs = rhs;
    this.operator = operator;
    this.workflowContext = workflowContext;
  }

  public write(writer: Writer): void {
    this.base.write(writer);
    writer.write(".");
    writer.write(this.operator);
    writer.write("(");
    this.lhs.write(writer);
    writer.write(", ");
    this.rhs.write(writer);
    writer.write(")");
  }
}
