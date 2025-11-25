import { python } from "@fern-api/python-ast";
import { isNil } from "lodash";

import { BaseNodeInputWorkflowReference } from "./BaseNodeInputWorkflowReference";

import { AstNode } from "src/generators/extensions/ast-node";
import { StrInstantiation } from "src/generators/extensions/str-instantiation";
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
      // Filter out entries with None values to avoid generating =None parameters
      const classArguments = entries
        .filter((entry) => !isConstantNullValue(entry.value))
        .map((entry) => {
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
      const keyAstNode = new StrInstantiation(entry.key);

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

function isConstantNullValue(
  valueDescriptor: DictionaryWorkflowReferenceType["entries"][number]["value"]
): boolean {
  return (
    valueDescriptor?.type === "CONSTANT_VALUE" &&
    valueDescriptor.value?.type === "JSON" &&
    isNil(valueDescriptor.value.value)
  );
}
