import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { WorkflowContext } from "src/context";
import { NodeAttributeGenerationError } from "src/generators/errors";

export declare namespace BinaryExpression {
  interface Args {
    lhs: AstNode;
    rhs?: AstNode | undefined;
    operator: string;
    workflowContext: WorkflowContext;
  }
}

export class BinaryExpression extends AstNode {
  private readonly lhs: AstNode;
  private readonly rhs?: AstNode | undefined;
  private readonly operator: string;
  private readonly workflowContext: WorkflowContext;

  constructor({ lhs, rhs, operator, workflowContext }: BinaryExpression.Args) {
    super();
    this.lhs = lhs;
    this.rhs = rhs;
    this.operator = operator;
    this.workflowContext = workflowContext;
  }

  public write(writer: Writer): void {
    if (this.operator === "access_field") {
      this.lhs.write(writer);
      writer.write("[");
      if (this.rhs) {
        this.rhs.write(writer);
      } else {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            "rhs must be defined for access_field expressions"
          )
        );
        writer.write('""');
      }
      writer.write("]");
      return;
    }

    this.lhs.write(writer);

    let openParenthesis = false;
    if (this.operator === "or") {
      writer.write(" | ");
    } else if (this.operator === "and") {
      writer.write(" & ");
    } else if (this.operator === "+") {
      writer.write(".add(");
      openParenthesis = true;
    } else if (this.operator === "-") {
      writer.write(".minus(");
      openParenthesis = true;
    } else {
      writer.write(`.${this.operator}(`);
      openParenthesis = true;
    }

    if (this.rhs) {
      this.rhs.write(writer);
    }
    if (openParenthesis) {
      writer.write(")");
    }
  }
}
