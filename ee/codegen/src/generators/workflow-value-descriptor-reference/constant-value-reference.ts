import { AstNode } from "@fern-api/python-ast/core/AstNode";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { BaseNodeInputWorkflowReference } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReference";
import {
  ConstantValueWorkflowReference as ConstantValueWorkflowReferenceType,
  IterableConfig,
} from "src/types/vellum";

export declare namespace ConstantValueReference {
  interface Args {
    workflowContext: WorkflowContext;
    nodeInputWorkflowReferencePointer: ConstantValueWorkflowReferenceType;
    iterableConfig?: IterableConfig;
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
    });
  }
}
