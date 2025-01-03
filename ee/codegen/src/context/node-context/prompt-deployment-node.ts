import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { PromptNode } from "src/types/vellum";

export class PromptDeploymentNodeContext extends BaseNodeContext<PromptNode> {
  baseNodeClassName = "PromptDeploymentNode";
  baseNodeDisplayClassName = "BasePromptDeploymentNodeDisplay";

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
