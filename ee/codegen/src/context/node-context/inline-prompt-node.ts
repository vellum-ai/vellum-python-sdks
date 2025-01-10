import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { InlinePromptNode as InlinePromptNodeType } from "src/types/vellum";

export class InlinePromptNodeContext extends BaseNodeContext<InlinePromptNodeType> {
  baseNodeClassName = "InlinePromptNode";
  baseNodeDisplayClassName = "BaseInlinePromptNodeDisplay";

  protected getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.outputId]: "text",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "error" }
        : {}),
      [this.nodeData.data.arrayOutputId]: "results",
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
