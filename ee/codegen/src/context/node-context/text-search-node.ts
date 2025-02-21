import { DocumentIndexRead } from "vellum-ai/api";
import { DocumentIndexes as DocumentIndexesClient } from "vellum-ai/api/resources/documentIndexes/client/Client";
import { VellumError } from "vellum-ai/errors";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { EntityNotFoundError } from "src/generators/errors";
import { SearchNode } from "src/types/vellum";

export class TextSearchNodeContext extends BaseNodeContext<SearchNode> {
  baseNodeClassName = "SearchNode";
  baseNodeDisplayClassName = "BaseSearchNodeDisplay";
  documentIndex: DocumentIndexRead | null = null;

  getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.resultsOutputId]: "results",
      [this.nodeData.data.textOutputId]: "text",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "error" }
        : {}),
    };
  }

  createPortContexts(): PortContext[] {
    return [
      new PortContext({
        workflowContext: this.workflowContext,
        nodeContext: this,
        portId: this.nodeData.data.sourceHandleId,
      }),
    ];
  }

  async buildProperties(): Promise<void> {
    // Grab the associated document index from api if available to always populate document_index field
    // with name instead of ID. We can only do this if the document index input is a constant value.
    let documentIndex: DocumentIndexRead | null = null;
    const inputValue = this.nodeData.inputs.find(
      (input) => input.id === this.nodeData.data.documentIndexNodeInputId
    )?.value;

    const rule = inputValue?.rules?.[0];
    if (rule?.type === "CONSTANT_VALUE") {
      if (rule.data.value?.toString()) {
        try {
          documentIndex = await new DocumentIndexesClient({
            apiKey: this.workflowContext.vellumApiKey,
          }).retrieve(rule.data.value?.toString());
        } catch (e) {
          if (e instanceof VellumError && e.statusCode === 404) {
            this.workflowContext.addError(
              new EntityNotFoundError(
                `Document Index "${rule.data.value?.toString()}" not found.`,
                "WARNING"
              )
            );
          } else {
            throw e;
          }
        }
      }
    }

    this.documentIndex = documentIndex;
  }
}
