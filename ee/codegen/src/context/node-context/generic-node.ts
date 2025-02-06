import { BaseNodeContext } from "src/context/node-context/base";
import { PortContext } from "src/context/port-context";
import { GenericNode as GenericNodeType } from "src/types/vellum";

export class GenericNodeContext extends BaseNodeContext<GenericNodeType> {
  baseNodeClassName = "BaseNode";
  baseNodeDisplayClassName = "BaseNodeDisplay";

  getNodeOutputNamesById(): Record<string, string> {
    return Object.fromEntries(
      this.nodeData.outputs.map((output) => [output.id, output.name])
    );
  }

  createPortContexts(): PortContext[] {
    return this.nodeData.ports.map(
      (port) =>
        new PortContext({
          workflowContext: this.workflowContext,
          nodeContext: this,
          portId: port.id,
          portName: port.name,
          isDefault: port.type === "DEFAULT",
        })
    );
  }
}
