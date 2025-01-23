import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { ApiNode as ApiNodeType } from "src/types/vellum";

export class ApiNodeContext extends BaseNodeContext<ApiNodeType> {
  baseNodeClassName = "APINode";
  baseNodeDisplayClassName = "BaseAPINodeDisplay";

  getNodeOutputNamesById(): Record<string, string> {
    return {
      [this.nodeData.data.jsonOutputId]: "json",
      [this.nodeData.data.statusCodeOutputId]: "status_code",
      [this.nodeData.data.textOutputId]: "text",
      ...(this.nodeData.data.errorOutputId
        ? { [this.nodeData.data.errorOutputId]: "error" }
        : {}),
    };
  }

  protected createPortContexts(): PortContext[] {
    return [
      new PortContext({
        workflowContext: this.workflowContext,
        nodeContext: this,
        portId: this.nodeData.data.sourceHandleId,
      }),
    ];
  }
}
