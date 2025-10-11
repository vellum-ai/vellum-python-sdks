import { VellumVariableType } from "vellum-ai/api";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { TemplatingNode } from "src/types/vellum";

export class TemplatingNodeContext extends BaseNodeContext<TemplatingNode> {
  baseNodeClassName = "TemplatingNode";
  baseNodeDisplayClassName = "BaseTemplatingNodeDisplay";
  isCore = true;

  public getNodeOutputNamesById(): Record<string, string> {
    const errorOutputId = this.getErrorOutputId();
    return {
      [this.nodeData.data.outputId]: "result",
      ...(errorOutputId ? { [errorOutputId]: "error" } : {}),
    };
  }

  protected getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {
      [this.nodeData.data.outputId]: this.nodeData.data.outputType,
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "ERROR" }
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
