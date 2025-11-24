import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { BaseNodeContext } from "src/context/node-context/base";
import { AstNode } from "src/generators/extensions/ast-node";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import {
  AttributeConfig,
  ConstantValueWorkflowReference as ConstantValueWorkflowReferenceType,
  IterableConfig,
  WorkflowDataNode,
} from "src/types/vellum";

export declare namespace ConstantValueReference {
  interface Args {
    nodeContext?: BaseNodeContext<WorkflowDataNode>;
    workflowContext: WorkflowContext;
    nodeInputWorkflowReferencePointer: ConstantValueWorkflowReferenceType;
    iterableConfig?: IterableConfig;
    attributeConfig?: AttributeConfig;
  }
}

export class ConstantValueReference extends BaseNodeInputWorkflowReference<ConstantValueWorkflowReferenceType> {
  constructor(args: ConstantValueReference.Args) {
    super(args);
  }

  getAstNode(): AstNode | undefined {
    const constantValueReferencePointer =
      this.nodeInputWorkflowReferencePointer.value;

    return codegen.vellumValue({
      vellumValue: constantValueReferencePointer,
      iterableConfig: this.iterableConfig,
      attributeConfig: this.attributeConfig,
    });
  }
}
