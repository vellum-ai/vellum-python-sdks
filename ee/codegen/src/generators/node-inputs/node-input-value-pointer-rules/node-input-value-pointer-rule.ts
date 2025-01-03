import { AstNode } from "@fern-api/python-ast/core/AstNode";
import { Writer } from "@fern-api/python-ast/core/Writer";

import { BaseNodeInputValuePointerRule } from "./base";
import { ConstantValuePointerRule } from "./constant-value-pointer";
import { InputVariablePointerRule } from "./input-variable-pointer";
import { NodeOutputPointerRule } from "./node-output-pointer";

import { WorkflowContext } from "src/context";
import { ExecutionCounterPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/execution-counter-pointer";
import { WorkspaceSecretPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/workspace-secret-pointer";
import { NodeInputValuePointerRule as NodeInputValuePointerRuleType } from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export declare namespace NodeInputValuePointerRule {
  export interface Args {
    workflowContext: WorkflowContext;
    nodeInputValuePointerRuleData: NodeInputValuePointerRuleType;
  }
}

export class NodeInputValuePointerRule extends AstNode {
  private workflowContext: WorkflowContext;
  private astNode: BaseNodeInputValuePointerRule<NodeInputValuePointerRuleType>;
  public readonly ruleType: NodeInputValuePointerRuleType["type"];

  public constructor(args: NodeInputValuePointerRule.Args) {
    super();
    this.workflowContext = args.workflowContext;
    this.ruleType = args.nodeInputValuePointerRuleData.type;

    this.astNode = this.getAstNode(args.nodeInputValuePointerRuleData);
    this.inheritReferences(this.astNode);
  }

  private getAstNode(
    nodeInputValuePointerRuleData: NodeInputValuePointerRuleType
  ): BaseNodeInputValuePointerRule<NodeInputValuePointerRuleType> {
    const ruleType = nodeInputValuePointerRuleData.type;

    switch (ruleType) {
      case "CONSTANT_VALUE":
        return new ConstantValuePointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "NODE_OUTPUT":
        return new NodeOutputPointerRule({
          workflowContext: this.workflowContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
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
    this.astNode.write(writer);
  }
}
