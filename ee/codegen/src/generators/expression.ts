import { python } from "@fern-api/python-ast";
import { TypeInstantiation } from "@fern-api/python-ast/TypeInstantiation";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { VELLUM_WORKFLOW_CONSTANTS_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { NodeAttributeGenerationError } from "src/generators/errors";
import { WorkflowValueDescriptorReference } from "src/generators/workflow-value-descriptor-reference/workflow-value-descriptor-reference";

export declare namespace Expression {
  interface Args {
    lhs: AstNode;
    operator: string;
    rhs?: AstNode | undefined;
    base?: AstNode | undefined;
    workflowContext: WorkflowContext;
  }
}

type NodeInput = AstNode & {
  nodeInputValuePointer: {
    nodeInputValuePointerData?: {
      rules?: Array<{ type: string }>;
    };
  };
};

// This is to replace the usage of instanceof when checking for NodeInput
// due to a circular dependency
function isNodeInput(node: AstNode): node is NodeInput {
  return (
    node != null &&
    "nodeInputValuePointer" in node &&
    node.nodeInputValuePointer != null &&
    typeof node.nodeInputValuePointer === "object"
  );
}

export class Expression extends AstNode {
  private readonly astNode: AstNode;
  private readonly workflowContext: WorkflowContext;
  constructor({ lhs, operator, rhs, base, workflowContext }: Expression.Args) {
    super();
    this.astNode = this.generateAstNode({ lhs, operator, rhs, base });
    this.workflowContext = workflowContext;
  }

  private generateAstNode({
    lhs,
    operator,
    rhs,
    base,
  }: Omit<Expression.Args, "workflowContext">): AstNode {
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
    let rawLhs = base;
    if (!rhs) {
      throw new NodeAttributeGenerationError(
        "rhs must be defined if base is defined"
      );
    }
    if (
      this.isConstantValueReference(base) ||
      this.isConstantValuePointer(base)
    ) {
      rawLhs = this.generateLhsAsConstantReference(base);
    }
    this.inheritReferences(rawLhs);
    return `${rawLhs.toString()}.${operator}(${lhs.toString()}, ${rhs.toString()})`;
  }

  private generateStandardExpression(
    lhs: AstNode,
    operator: string,
    rhs: AstNode | undefined
  ): string {
    let rawLhs = lhs;
    if (
      this.isConstantValueReference(lhs) ||
      this.isConstantValuePointer(lhs) ||
      this.isTypeInstantiation(lhs)
    ) {
      rawLhs = this.generateLhsAsConstantReference(lhs);
    }
    this.inheritReferences(rawLhs);

    if (operator === "access_field") {
      if (!rhs) {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            "rhs must be defined if operator is access_field"
          )
        );
        return `${rawLhs.toString()}[""]`;
      }
      return `${rawLhs.toString()}[${rhs.toString()}]`;
    }

    const rhsExpression = rhs ? `(${rhs.toString()})` : "()";

    if (operator === "or") {
      return `${rawLhs.toString()} | ${rhsExpression}`;
    } else if (operator === "and") {
      return `${rawLhs.toString()} & ${rhsExpression}`;
    } else if (operator === "+") {
      return `${rawLhs.toString()}.add${rhsExpression}`;
    } else if (operator === "-") {
      return `${rawLhs.toString()}.minus${rhsExpression}`;
    }
    return `${rawLhs.toString()}.${operator}${rhsExpression}`;
  }

  // We are assuming that the expression contains "good data". If the expression contains data
  // where the generated expression is not correct, update the logic here with guardrails similar to the UI
  private generateLhsAsConstantReference(lhs: AstNode): AstNode {
    const constantValueReference = python.reference({
      name: "ConstantValueReference",
      modulePath: VELLUM_WORKFLOW_CONSTANTS_PATH,
    });
    return python.instantiateClass({
      classReference: constantValueReference,
      arguments_: [
        python.methodArgument({
          value: lhs,
        }),
      ],
    });
  }

  private isConstantValueReference(lhs: AstNode): boolean {
    return (
      lhs instanceof WorkflowValueDescriptorReference &&
      lhs.workflowValueReferencePointer === "CONSTANT_VALUE"
    );
  }

  private isConstantValuePointer(lhs: AstNode): boolean {
    if (!isNodeInput(lhs)) {
      return false;
    }

    return (
      lhs.nodeInputValuePointer.nodeInputValuePointerData?.rules != null &&
      lhs.nodeInputValuePointer.nodeInputValuePointerData.rules.length > 0 &&
      lhs.nodeInputValuePointer.nodeInputValuePointerData.rules[0]?.type ===
        "CONSTANT_VALUE"
    );
  }

  private isTypeInstantiation(lhs: AstNode): boolean {
    return lhs instanceof TypeInstantiation;
  }

  public write(writer: Writer) {
    this.astNode.write(writer);
  }
}
