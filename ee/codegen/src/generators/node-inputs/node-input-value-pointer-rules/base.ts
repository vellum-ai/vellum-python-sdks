import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { AstNode } from "src/generators/extensions/ast-node";
import { Writer } from "src/generators/extensions/writer";
import {
  IterableConfig,
  NodeInputValuePointerRule as NodeInputValuePointerRuleType,
  WorkflowDataNode,
} from "src/types/vellum";

export declare namespace BaseNodeInputValuePointerRule {
  export interface Args<T extends NodeInputValuePointerRuleType> {
    nodeContext: BaseNodeContext<WorkflowDataNode>;
    nodeInputValuePointerRule: T;
    iterableConfig?: IterableConfig;
  }
}

export abstract class BaseNodeInputValuePointerRule<
  T extends NodeInputValuePointerRuleType
> extends AstNode {
  protected readonly nodeContext: BaseNodeContext<WorkflowDataNode>;
  public readonly workflowContext: WorkflowContext;
  public readonly nodeInputValuePointerRule: T;
  public readonly iterableConfig?: IterableConfig;
  private astNode: AstNode | undefined;

  constructor({
    nodeContext,
    nodeInputValuePointerRule,
    iterableConfig,
  }: BaseNodeInputValuePointerRule.Args<T>) {
    super();
    this.nodeContext = nodeContext;
    this.workflowContext = nodeContext.workflowContext;
    this.iterableConfig = iterableConfig;
    this.nodeInputValuePointerRule = nodeInputValuePointerRule;

    this.astNode = this.getAstNode();
    if (this.astNode) {
      this.inheritReferences(this.astNode);
    }
  }

  public getReferencedNodeContext():
    | BaseNodeContext<WorkflowDataNode>
    | undefined {
    return undefined;
  }

  abstract getAstNode(): AstNode | undefined;

  public write(writer: Writer): void {
    if (this.astNode) {
      this.astNode.write(writer);
    }
  }
}
