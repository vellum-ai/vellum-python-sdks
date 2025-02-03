import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";
import { isNil } from "lodash";

import { NodeInputValuePointerRule } from "./node-input-value-pointer-rules/node-input-value-pointer-rule";

import { BaseNodeContext } from "src/context/node-context/base";
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

  public constructor(args: NodeInputValuePointer.Args) {
    super();

    this.nodeContext = args.nodeContext;
    this.nodeInputValuePointerData = args.nodeInputValuePointerData;

    this.rules = this.generateRules();
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

  write(writer: Writer): void {
    const firstRule = this.rules[0];
    if (!firstRule) {
      writer.write("None");
      return;
    }

    firstRule.write(writer);

    for (let i = 1; i < this.rules.length; i++) {
      const rule = this.rules[i];
      if (!rule) {
        continue;
      }

      const previousRule = this.rules[i - 1];
      if (previousRule && previousRule.ruleType === "CONSTANT_VALUE") {
        break;
      }

      writer.write(".coalesce(");
      rule.write(writer);
      writer.write(")");
    }
  }
}
