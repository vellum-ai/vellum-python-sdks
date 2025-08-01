import { VellumError } from "vellum-ai/errors";

import {
  WorkflowDataNode,
  WorkflowNode,
  ToolArgs as FunctionsType,
} from "src/types/vellum";

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

export function getCallableFunctions(
  nodeData: WorkflowDataNode
): FunctionsType | undefined {
  const functionsAttribute = nodeData.attributes?.find(
    (attr) => attr.name === "functions"
  );

  if (
    functionsAttribute?.value?.type === "CONSTANT_VALUE" &&
    functionsAttribute.value.value?.type === "JSON" &&
    Array.isArray(functionsAttribute.value.value.value) &&
    functionsAttribute.value.value.value.length > 0
  ) {
    return functionsAttribute.value.value.value as FunctionsType;
  }

  return undefined;
}
