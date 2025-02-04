import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { NodeAttributeGenerationError } from "src/generators/errors";
import { WorkflowValueDescriptorReference } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference";

export declare namespace Expression {
  interface Args {
    lhs: AstNode;
    operator: string;
    rhs?: AstNode | undefined;
    base?: AstNode | undefined;
  }
}

export class Expression extends AstNode {
  private readonly astNode: AstNode;

  constructor({ lhs, operator, rhs, base }: Expression.Args) {
    super();
    this.astNode = this.generateAstNode({ lhs, operator, rhs, base });
  }

  private generateAstNode({
    lhs,
    operator,
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
      ? this.generateExpressionWithBase(base, operator, lhs, rhs)
      : this.generateStandardExpression(lhs, operator, rhs);

    return python.codeBlock(rawExpression);
  }

  private generateExpressionWithBase(
    base: AstNode,
    operator: string,
    lhs: AstNode,
    rhs: AstNode | undefined
  ): string {
    if (!rhs) {
      throw new NodeAttributeGenerationError(
        "rhs must be defined if base is defined"
      );
    }
    if (this.isConstantValueReference(base)) {
      return this.generateExpressionBeginningWithConstantReference(
        lhs,
        operator,
        rhs,
        base
      );
    }
    this.inheritReferences(base);
    return `${base.toString()}.${operator}(${lhs.toString()}, ${rhs.toString()})`;
  }

  private generateStandardExpression(
    lhs: AstNode,
    operator: string,
    rhs: AstNode | undefined
  ): string {
    if (this.isConstantValueReference(lhs)) {
      return this.generateExpressionBeginningWithConstantReference(
        lhs,
        operator,
        rhs
      );
    }
    const rhsExpression = rhs ? `(${rhs.toString()})` : "()";
    return `${lhs.toString()}.${operator}${rhsExpression}`;
  }

  // We are assuming that the expression contains "good data". If the expression contains data
  // where the generated expression is not correct, update the logic here with guardrails similar to the UI
  private generateExpressionBeginningWithConstantReference(
    lhs: AstNode,
    operator: string,
    rhs: AstNode | undefined,
    base?: AstNode | undefined
  ): string {
    if (operator === "between" || operator === "notBetween") {
      return operator === "between"
        ? `${lhs.toString()} <= ${base?.toString()} <= ${rhs?.toString()}`
        : `${base?.toString()} < ${lhs.toString()} or ${base?.toString()} > ${rhs?.toString()}`;
    } else if (operator === "in" || operator === "notIn") {
      return operator === "in"
        ? `${lhs.toString()} in ${rhs?.toString()}`
        : `${lhs.toString()} not in ${rhs?.toString()}`;
    } else if (operator === "contains" || operator === "doesNotContain") {
      return operator === "contains"
        ? `${rhs?.toString()} in ${lhs.toString()}`
        : `${rhs?.toString()} not in ${lhs.toString()}`;
    } else if (operator === "startswith" || operator === "endswith") {
      return `${lhs.toString()}.${operator}(${rhs ? rhs.toString() : ""})`;
    } else if (operator === "null" || operator === "notNull") {
      return operator === "null"
        ? `${lhs.toString()} is None`
        : `${lhs.toString()} is not None`;
    } else if (
      operator === "doesNotBeginWith" ||
      operator === "doesNotEndWith"
    ) {
      return operator === "doesNotBeginWith"
        ? `!${lhs.toString()}.startswith(${rhs ? rhs.toString() : ""})`
        : `!${lhs.toString()}.endswith(${rhs ? rhs.toString() : ""})`;
    } else {
      const rhsExpression = rhs ? ` ${operator} ${rhs.toString()}` : "";
      return `${lhs.toString()}${rhsExpression}`;
    }
  }

  private isConstantValueReference(lhs: AstNode): boolean {
    return (
      lhs instanceof WorkflowValueDescriptorReference &&
      lhs.workflowValueReferencePointer === "CONSTANT_VALUE"
    );
  }

  public write(writer: Writer) {
    this.astNode.write(writer);
  }
}
