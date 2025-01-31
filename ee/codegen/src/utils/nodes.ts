import { WorkflowNode } from "src/types/vellum";

export function getNodeLabel(nodeData: WorkflowNode): string {
  switch (nodeData.type) {
    case "GENERIC":
      return nodeData.definition?.name ?? "Generic Node";
    default:
      return nodeData.data.label;
  }
}

export function isUnaryOperator(operator: string): boolean {
  return operator === "null" || operator === "notNull";
}
