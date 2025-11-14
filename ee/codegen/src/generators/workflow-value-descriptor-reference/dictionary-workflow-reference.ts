import { python } from "@fern-api/python-ast";
import { AstNode } from "@fern-api/python-ast/core/AstNode";

import { BaseNodeInputWorkflowReference } from "./BaseNodeInputWorkflowReference";

import { WorkflowValueDescriptor } from "src/generators/workflow-value-descriptor";
import { DictionaryWorkflowReference as DictionaryWorkflowReferenceType } from "src/types/vellum";

export class DictionaryWorkflowReference extends BaseNodeInputWorkflowReference<DictionaryWorkflowReferenceType> {
  getAstNode(): AstNode | undefined {
    const dictionaryReference = this.nodeInputWorkflowReferencePointer;
    const entries = dictionaryReference.entries;
    const definition = dictionaryReference.definition;

    if (!entries || entries.length === 0) {
      return python.TypeInstantiation.dict([]);
    }

    // If definition exists, generate class instantiation instead of dict
    if (definition) {
      const classArguments = entries.map((entry) => {
        const valueNode = new WorkflowValueDescriptor({
          nodeContext: this.nodeContext,
          workflowContext: this.workflowContext,
          workflowValueDescriptor: entry.value,
          iterableConfig: this.iterableConfig,
          attributeConfig: this.attributeConfig,
        });

        return python.methodArgument({
          name: entry.key,
          value: valueNode,
        });
      });

      return python.instantiateClass({
        classReference: python.reference({
          name: definition.name,
          modulePath: definition.module,
        }),
        arguments_: classArguments,
      });
    }

    // Otherwise, generate dict as before
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
