import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputValuePointerRule } from "./base";
import { ConstantValuePointerRule } from "./constant-value-pointer";
import { EnvironmentVariablePointerRule } from "./environment-variable-pointer";
import { InputVariablePointerRule } from "./input-variable-pointer";
import { NodeOutputPointerRule } from "./node-output-pointer";
import { WorkflowStatePointerRule } from "./workflow-state-pointer";

import { BaseNodeContext } from "src/context/node-context/base";
import { Writer } from "src/generators/extensions/writer";
import { ExecutionCounterPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/execution-counter-pointer";
import { WorkspaceSecretPointerRule } from "src/generators/node-inputs/node-input-value-pointer-rules/workspace-secret-pointer";
import {
  IterableConfig,
  NodeInputValuePointerRule as NodeInputValuePointerRuleType,
  WorkflowDataNode,
} from "src/types/vellum";
import { assertUnreachable } from "src/utils/typing";

export declare namespace NodeInputValuePointerRule {
  export interface Args {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    nodeInputValuePointerRuleData: NodeInputValuePointerRuleType;
    iterableConfig?: IterableConfig;
  }
}

export class NodeInputValuePointerRule extends AstNode {
  private nodeContext: BaseNodeContext<WorkflowDataNode>;
  public astNode:
    | BaseNodeInputValuePointerRule<NodeInputValuePointerRuleType>
    | undefined;
  public readonly ruleType: NodeInputValuePointerRuleType["type"];
  private iterableConfig?: IterableConfig;

  public constructor(args: NodeInputValuePointerRule.Args) {
    super();
    this.nodeContext = args.nodeContext;
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
          nodeContext: this.nodeContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
          iterableConfig: this.iterableConfig,
        });
      case "NODE_OUTPUT": {
        const rule = new NodeOutputPointerRule({
          nodeContext: this.nodeContext,
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
          nodeContext: this.nodeContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "WORKSPACE_SECRET":
        return new WorkspaceSecretPointerRule({
          nodeContext: this.nodeContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "EXECUTION_COUNTER":
        return new ExecutionCounterPointerRule({
          nodeContext: this.nodeContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "ENVIRONMENT_VARIABLE":
        return new EnvironmentVariablePointerRule({
          nodeContext: this.nodeContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      case "WORKFLOW_STATE":
        return new WorkflowStatePointerRule({
          nodeContext: this.nodeContext,
          nodeInputValuePointerRule: nodeInputValuePointerRuleData,
        });
      default: {
        assertUnreachable(ruleType);
      }
    }
  }

  public getReferencedNodeContext():
    | BaseNodeContext<WorkflowDataNode>
    | undefined {
    return this.astNode?.getReferencedNodeContext();
  }

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
