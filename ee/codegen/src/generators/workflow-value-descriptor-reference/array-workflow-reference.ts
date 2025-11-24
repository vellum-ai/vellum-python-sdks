import { python } from "@fern-api/python-ast";

import { BaseNodeInputWorkflowReference } from "./BaseNodeInputWorkflowReference";

import { AstNode } from "src/generators/extensions/ast-node";
import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { ArrayWorkflowReference as ArrayWorkflowReferenceType } from "src/types/vellum";

export class ArrayWorkflowReference extends BaseNodeInputWorkflowReference<ArrayWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const arrayReference = this.nodeInputWorkflowReferencePointer;
    const items = arrayReference.items;

    if (!items || items.length === 0) {
      return python.TypeInstantiation.list([]);
    }

    const listItems = items.map((item) => {
      const valueNode = new WorkflowValueDescriptor({
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
        workflowValueDescriptor: item,
        iterableConfig: this.iterableConfig,
        attributeConfig: this.attributeConfig,
      });

      return valueNode;
    });

    return python.TypeInstantiation.list(listItems, {
      endWithComma: true,
    });
  }
}
