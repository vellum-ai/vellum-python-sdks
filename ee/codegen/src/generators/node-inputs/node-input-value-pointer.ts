import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { NodeInputValuePointerRule } from "./node-input-value-pointer-rules/node-input-value-pointer-rule";

import { BaseNodeContext } from "src/context/node-context/base";
import { StaticMethodInvocation } from "src/generators/static-method-invocation";
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
  private nodeInputValuePointerData: NodeInputValuePointerType;

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
        const rule = new NodeInputValuePointerRule({
          nodeContext: this.nodeContext,
          nodeInputValuePointerRuleData: ruleData,
        });
        if (rule.astNode) {
          this.inheritReferences(rule);
          return rule;
        }
        return undefined;
      })
      .filter((rule) => !isNil(rule));
  }

  private generateAstNode(): AstNode {
    const rules = this.rules;

    const firstRule = rules[0];
    if (!firstRule) {
      return python.TypeInstantiation.none();
    }

    let expression: AstNode = firstRule;

    for (let i = 1; i < rules.length; i++) {
      const rule = rules[i];
      if (!rule) {
        continue;
      }

      const previousRule = rules[i - 1];
      if (previousRule && previousRule.ruleType === "CONSTANT_VALUE") {
        break;
      }

      expression = new StaticMethodInvocation({
        reference: expression,
        methodName: "coalesce",
        arguments_: [python.methodArgument({ value: rule })],
      });
    }

    const hasReferenceToSelf = this.hasReferenceToSelf(rules);
    if (hasReferenceToSelf) {
      const lazyReference = python.instantiateClass({
        classReference: python.reference({
          name: "LazyReference",
          modulePath: [
            ...this.nodeContext.workflowContext.sdkModulePathNames
              .WORKFLOWS_MODULE_PATH,
            "references",
          ],
        }),
        arguments_: [
          python.methodArgument({
            value: python.lambda({
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

  write(writer: Writer): void {
    this.astNode.write(writer);
  }
}
