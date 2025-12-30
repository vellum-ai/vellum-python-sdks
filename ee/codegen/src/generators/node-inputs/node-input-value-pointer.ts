import { isNil } from "lodash";

import { NodeInputValuePointerRule } from "./node-input-value-pointer-rules/node-input-value-pointer-rule";

import { VELLUM_WORKFLOW_CONSTANTS_PATH } from "src/constants";
import { BaseNodeContext } from "src/context/node-context/base";
import { BaseCodegenError } from "src/generators/errors";
import { AccessAttribute } from "src/generators/extensions/access-attribute";
import { AstNode } from "src/generators/extensions/ast-node";
import { ClassInstantiation } from "src/generators/extensions/class-instantiation";
import { LambdaInstantiation } from "src/generators/extensions/lambda-instantiation";
import { MethodArgument } from "src/generators/extensions/method-argument";
import { MethodInvocation } from "src/generators/extensions/method-invocation";
import { NoneInstantiation } from "src/generators/extensions/none-instantiation";
import { Reference } from "src/generators/extensions/reference";
import { TypeInstantiation } from "src/generators/extensions/type-instantiation";
import { Writer } from "src/generators/extensions/writer";
import {
  NodeInputValuePointer as NodeInputValuePointerType,
  WorkflowDataNode,
} from "src/types/vellum";

export declare namespace NodeInputValuePointer {
  export interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    nodeInputValuePointerData: NodeInputValuePointerType;
  }
}

export class NodeInputValuePointer extends AstNode {
  private nodeContext: BaseNodeContext<WorkflowDataNode>;
  public readonly nodeInputValuePointerData: NodeInputValuePointerType;

  public rules: NodeInputValuePointerRule[];
  private astNode: AstNode;

  public constructor(args: NodeInputValuePointer.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.nodeInputValuePointerData = args.nodeInputValuePointerData;

    this.rules = this.generateRules();

    const astNode = this.generateAstNode();
    this.inheritReferences(astNode);

    this.astNode = astNode;
  }

  private generateRules(): NodeInputValuePointerRule[] {
    return this.nodeInputValuePointerData.rules
      .map((ruleData) => {
        try {
          const rule = new NodeInputValuePointerRule({
            nodeContext: this.nodeContext,
            nodeInputValuePointerRuleData: ruleData,
          });
          if (rule.astNode) {
            this.inheritReferences(rule);
            return rule;
          }
        } catch (error) {
          if (error instanceof BaseCodegenError) {
            this.nodeContext.workflowContext.addError(error);
          } else {
            throw error;
          }
        }
        return undefined;
      })
      .filter((rule): rule is NodeInputValuePointerRule => !isNil(rule));
  }

  private generateAstNode(): AstNode {
    const rules = this.rules;

    const firstRule = rules[0];
    if (!firstRule) {
      return new NoneInstantiation();
    }

    let expression: AstNode = firstRule;

    // If the first rule is a TypeInstantiation (e.g., NoneInstantiation from an unresolvable reference)
    // and there are more rules to coalesce with, wrap it in ConstantValueReference
    // to avoid generating invalid code like `None.coalesce("fallback")`
    const firstRuleAstNode = firstRule.astNode?.getAstNode();
    if (rules.length > 1 && firstRuleAstNode instanceof TypeInstantiation) {
      expression = this.wrapInConstantValueReference(firstRule);
    }

    for (let i = 1; i < rules.length; i++) {
      const rule = rules[i];
      if (!rule) {
        continue;
      }

      const previousRule = rules[i - 1];
      if (previousRule && previousRule.ruleType === "CONSTANT_VALUE") {
        break;
      }

      expression = new AccessAttribute({
        lhs: expression,
        rhs: new MethodInvocation({
          methodReference: new Reference({
            name: "coalesce",
          }),
          arguments_: [new MethodArgument({ value: rule })],
        }),
      });
    }

    const hasReferenceToSelf = this.hasReferenceToSelf(rules);
    if (hasReferenceToSelf) {
      const lazyReference = new ClassInstantiation({
        classReference: new Reference({
          name: "LazyReference",
          modulePath: [
            ...this.nodeContext.workflowContext.sdkModulePathNames
              .WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          new MethodArgument({
            value: new LambdaInstantiation({
              body: expression,
            }),
          }),
        ],
      });
      return lazyReference;
    } else {
      return expression;
    }
  }

  private hasReferenceToSelf(rules: NodeInputValuePointerRule[]): boolean {
    const referencedNodeContexts = new Set(
      rules
        .map((rule) => rule.getReferencedNodeContext())
        .filter((nodeContext) => !isNil(nodeContext))
    );

    return referencedNodeContexts.has(this.nodeContext);
  }

  private wrapInConstantValueReference(node: AstNode): AstNode {
    const constantValueReference = new Reference({
      name: "ConstantValueReference",
      modulePath: VELLUM_WORKFLOW_CONSTANTS_PATH,
    });
    return new ClassInstantiation({
      classReference: constantValueReference,
      arguments_: [
        new MethodArgument({
          value: node,
        }),
      ],
    });
  }

  write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
