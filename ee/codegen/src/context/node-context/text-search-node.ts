import { DocumentIndexRead } from "vellum-ai/api";

import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { SearchNode } from "src/types/vellum";

export declare namespace TextSearchNodeContext {
  interface Args extends BaseNodeContext.Args<SearchNode> {
    documentIndex: DocumentIndexRead | null;
  }
}

export class TextSearchNodeContext extends BaseNodeContext<SearchNode> {
  baseNodeClassName = "SearchNode";
  baseNodeDisplayClassName = "BaseSearchNodeDisplay";
  documentIndex: DocumentIndexRead | null;

  constructor(args: TextSearchNodeContext.Args) {
    super(args);
    this.documentIndex = args.documentIndex;
  }

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
}
