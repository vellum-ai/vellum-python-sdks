import { TypeInstantiation as FernTypeInstantiation } from "@fern-api/python-ast/TypeInstantiation";

import { NodeAttributeGenerationError } from "./errors";
import { BinaryExpression } from "./expressions/binary";
import { TernaryExpression } from "./expressions/ternary";

import { VELLUM_WORKFLOW_CONSTANTS_PATH } from "src/constants";
import { WorkflowContext } from "src/context";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";
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
    if (base) {
      let rawBase = base;
      if (
        this.isConstantValueReference(base) ||
        this.isConstantValuePointer(base) ||
        this.isTypeInstantiation(base)
      ) {
        rawBase = this.generateConstantReference(base);
      }
      this.inheritReferences(rawBase);

      let rawRhs = rhs;
      if (!rawRhs) {
        this.workflowContext.addError(
          new NodeAttributeGenerationError(
            "rhs must be defined for ternary expressions"
          )
        );
        rawRhs = new NoneInstantiation();
      }

      this.inheritReferences(rawRhs);
      this.inheritReferences(lhs);
      this.inheritReferences(rawBase);

      return new TernaryExpression({
        base: rawBase,
        lhs,
        rhs: rawRhs,
        operator,
        workflowContext: this.workflowContext,
      });
    }

    let rawLhs = lhs;
    if (
      this.isConstantValueReference(lhs) ||
      this.isConstantValuePointer(lhs) ||
      this.isTypeInstantiation(lhs)
    ) {
      rawLhs = this.generateConstantReference(lhs);
    }
    this.inheritReferences(rawLhs);
    this.inheritReferences(rhs);

    return new BinaryExpression({
      lhs: rawLhs,
      rhs,
      operator,
      workflowContext: this.workflowContext,
    });
  }

  // We are assuming that the expression contains "good data". If the expression contains data
  // where the generated expression is not correct, update the logic here with guardrails similar to the UI
  private generateConstantReference(ref: AstNode): AstNode {
    const constantValueReference = new Reference({
      name: "ConstantValueReference",
      modulePath: VELLUM_WORKFLOW_CONSTANTS_PATH,
    });
    return new ClassInstantiation({
      classReference: constantValueReference,
      arguments_: [
        new MethodArgument({
          value: ref,
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
    // Check for both our local TypeInstantiation (which NoneInstantiation, StrInstantiation, etc. extend)
    // and the fern TypeInstantiation for backwards compatibility
    return (
      lhs instanceof TypeInstantiation || lhs instanceof FernTypeInstantiation
    );
  }

  public write(writer: Writer) {
    this.astNode.write(writer);
  }
}
