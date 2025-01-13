import { BaseNodeContext } from "./base";

import { PortContext } from "src/context/port-context";
import { NodeDefinitionGenerationError } from "src/generators/errors";
import { MapNode as MapNodeType } from "src/types/vellum";

export class MapNodeContext extends BaseNodeContext<MapNodeType> {
  baseNodeClassName = "MapNode";
  baseNodeDisplayClassName = "BaseMapNodeDisplay";
  isCore = true;

  getNodeOutputNamesById(): Record<string, string> {
    const subworkflowNodeData = this.nodeData.data;
    if (subworkflowNodeData.variant !== "INLINE") {
      throw new NodeDefinitionGenerationError(
        `MapNode only supports INLINE variant. Received: ${this.nodeData.data.variant}`
      );
    }

    return subworkflowNodeData.outputVariables.reduce((acc, variable) => {
      acc[variable.id] = variable.key;
      return acc;
    }, {} as Record<string, string>);
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
