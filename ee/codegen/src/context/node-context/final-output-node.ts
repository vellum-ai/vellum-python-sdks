import { VellumVariableType } from "vellum-ai/api";

import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { FinalOutputNode } from "src/types/vellum";

export class FinalOutputNodeContext extends BaseNodeContext<FinalOutputNode> {
  baseNodeClassName = "FinalOutputNode";
  baseNodeDisplayClassName = "BaseFinalOutputNodeDisplay";

  public getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.outputId]: "value",
    };
  }

  protected getNodeOutputTypesById(): Record<string, VellumVariableType> {
    return {
      [this.nodeData.data.outputId]: this.nodeData.data.outputType,
    };
  }

  createPortContexts(): PortContext[] {
    return [];
  }
}
