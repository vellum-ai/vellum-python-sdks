import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { BaseNodeInputValuePointerRule } from "./base";
import { ConstantValuePointerRule } from "./constant-value-pointer";
import { InputVariablePointerRule } from "./input-variable-pointer";
import { NodeOutputPointerRule } from "./node-output-pointer";

import { WorkflowContext } from "src/context";
import { ExecutionCounterPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/execution-counter-pointer";
import { WorkspaceSecretPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/workspace-secret-pointer";
import {
  IterableConfig,
  NodeInputValuePointerRule as NodeInputValuePointerRuleType,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export declare namespace NodeInputValuePointerRule {
  export interface Args {
    workflowContext: WorkflowContext;
    nodeInputValuePointerRuleData: NodeInputValuePointerRuleType;
    iterableConfig?: IterableConfig;
  }
}

export class NodeInputValuePointerRule extends AstNode {
  private workflowContext: WorkflowContext;
  public astNode:
    | BaseNodeInputValuePointerRule<NodeInputValuePointerRuleType>
    | undefined;
  public readonly ruleType: NodeInputValuePointerRuleType["type"];
  private iterableConfig?: IterableConfig;

  public constructor(args: NodeInputValuePointerRule.Args) {
    super();
    this.workflowContext = args.workflowContext;
    this.ruleType = args.nodeInputValuePointerRuleData.type;
    this.iterableConfig = args.iterableConfig;

    this.astNode = this.getAstNode(args.nodeInputValuePointerRuleData);
    if (this.astNode) {
      this.inheritReferences(this.astNode);
    }
  }

  private getAstNode(
    nodeInputValuePointerRuleData: NodeInputValuePointerRuleType
  ): BaseNodeInputValuePointerRule<NodeInputValuePointerRuleType> | undefined {
    const ruleType = nodeInputValuePointerRuleData.type;

    switch (ruleType) {
      case "CONSTANT_VALUE":
        return new ConstantValuePointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
          iterableConfig: this.iterableConfig,
        });
      case "NODE_OUTPUT": {
        const rule = new NodeOutputPointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
        if (rule.getAstNode()) {
          return rule;
        } else {
          return undefined;
        }
      }
      case "INPUT_VARIABLE":
        return new InputVariablePointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "WORKSPACE_SECRET":
        return new WorkspaceSecretPointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "EXECUTION_COUNTER":
        return new ExecutionCounterPointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      default: {
        assertUnreachable(ruleType);
      }
    }
  }

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
