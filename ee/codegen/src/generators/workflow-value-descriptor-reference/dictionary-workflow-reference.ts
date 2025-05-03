import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReference } from "./BaseNodeInputWorkflowReference";

import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { DictionaryWorkflowReference as DictionaryWorkflowReferenceType } from "src/types/vellum";

export class DictionaryWorkflowReference extends BaseNodeInputWorkflowReference<DictionaryWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const dictionaryReference = this.nodeInputWorkflowReferencePointer;
    const entries = dictionaryReference.entries;

    if (!entries || entries.length === 0) {
      return python.TypeInstantiation.dict([]);
    }

    const dictEntries = entries.map((entry) => {
      const keyAstNode = python.TypeInstantiation.str(entry.key);

      const valueNode = new WorkflowValueDescriptor({
        nodeContext: this.nodeContext,
        workflowContext: this.workflowContext,
        workflowValueDescriptor: entry.value,
        iterableConfig: this.iterableConfig,
        attributeConfig: this.attributeConfig,
      });

      return {
        key: keyAstNode,
        value: valueNode,
      };
    });

    return python.TypeInstantiation.dict(dictEntries, {
      endWithComma: true,
    });
  }
}
