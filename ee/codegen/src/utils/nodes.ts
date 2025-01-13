import { NodeDefinitionGenerationError } from "src/generators/errors";
import { WorkflowNode } from "src/types/vellum";

export function getNodeId(nodeData: WorkflowNode): string {
  switch (nodeData.type) {
    case "GENERIC": {
      if (!nodeData.definition) {
        throw new NodeDefinitionGenerationError(
          "Generic node missing definition"
        );
      }
      const syntheticId = [
        ...nodeData.definition.module,
        nodeData.definition.name,
      ].join(".");
      return syntheticId;
    }
    default:
      return nodeData.id;
  }
}

export function getNodeLabel(nodeData: WorkflowNode): string {
  switch (nodeData.type) {
    case "GENERIC":
      return nodeData.definition?.name ?? "Generic Node";
    default:
      return nodeData.data.label;
  }
}
