import { WorkflowGenerationError } from "src/generators/errors";
import { WorkflowNode, WorkflowOutputValue } from "src/types/vellum";

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

export function getNodeIdFromNodeOutputWorkflowReference(
  workflowOutput: WorkflowOutputValue
): string {
  if (
    "type" in workflowOutput.value &&
    workflowOutput.value.type === "NODE_OUTPUT"
  ) {
    return workflowOutput.value.nodeId;
  } else {
    throw new WorkflowGenerationError(
      `Expected WorkflowOutputValue to be of type NODE_OUTPUT but got ${workflowOutput.value.type} instead`
    );
  }
}

export function getNodeOutputIdFromNodeOutputWorkflowReference(
  workflowOutput: WorkflowOutputValue
): string {
  if (
    "type" in workflowOutput.value &&
    workflowOutput.value.type === "NODE_OUTPUT"
  ) {
    return workflowOutput.value.nodeOutputId;
  } else {
    throw new WorkflowGenerationError(
      `Expected WorkflowOutputValue to be of type NODE_OUTPUT but got ${workflowOutput.value.type} instead`
    );
  }
}
