import { VellumError } from "vellum-ai/errors";

import { WorkflowNode } from "src/types/vellum";

export function getNodeLabel(nodeData: WorkflowNode): string {
  switch (nodeData.type) {
    case "GENERIC":
      return nodeData.definition?.name ?? nodeData.label ?? "Generic Node";
    default:
      return nodeData.data.label;
  }
}

export function isUnaryOperator(operator: string): boolean {
  return operator === "null" || operator === "notNull";
}

export function isVellumErrorWithDetail(
  error: unknown
): error is VellumError & { body: { detail: string } } {
  return (
    error instanceof VellumError &&
    typeof error.body === "object" &&
    error.body !== null &&
    "detail" in error.body &&
    typeof error.body.detail === "string"
  );
}
