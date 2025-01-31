import { AstNode } from "@fern-api/python-ast/core/AstNode";

import * as codegen from "src/codegen";
import { WorkflowContext } from "src/context";
import { BaseNodeInputWorkflowReferencePointer } from "src/generators/workflow-value-descriptor-reference/BaseNodeInputWorkflowReferencePointer";
import {
  ConstantValueWorkflowReference as ConstantValueWorkflowReferenceType,
  IterableConfig,
} from "src/types/vellum";

export declare namespace ConstantValueReferencePointer {
  interface Args {
    workflowContext: WorkflowContext;
    nodeInputWorkflowReferencePointer: ConstantValueWorkflowReferenceType;
    iterableConfig?: IterableConfig;
  }
}

export class ConstantValueReferencePointer extends BaseNodeInputWorkflowReferencePointer<ConstantValueWorkflowReferenceType> {
  constructor(args: ConstantValueReferencePointer.Args) {
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
