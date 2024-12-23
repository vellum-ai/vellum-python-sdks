import { SDK_MODULE_PATHS } from "src/context/workflow-context/types";

export function generateSdkModulePaths(
  workflowsSdkModulePath: Readonly<string[]>
): SDK_MODULE_PATHS {
  const nodesModulePath = [...workflowsSdkModulePath, "nodes"] as const;

  return {
    WORKFLOWS_MODULE_PATH: workflowsSdkModulePath,
    WORKFLOWS_DISPLAY_MODULE_PATH: [
      "vellum_ee",
      "workflows",
      "display",
      "workflows",
      "vellum_workflow_display",
    ] as const,
    CORE_NODES_MODULE_PATH: [...nodesModulePath, "core"] as const,
    DISPLAYABLE_NODES_MODULE_PATH: [...nodesModulePath, "displayable"] as const,
    INPUTS_MODULE_PATH: [...workflowsSdkModulePath, "inputs"] as const,
    SANDBOX_RUNNER_MODULE_PATH: [...workflowsSdkModulePath, "sandbox"] as const,
    STATE_MODULE_PATH: [...workflowsSdkModulePath, "state"] as const,
    NODE_DISPLAY_MODULE_PATH: [
      "vellum_ee",
      "workflows",
      "display",
      "nodes",
    ] as const,
    NODE_DISPLAY_TYPES_MODULE_PATH: [
      "vellum_ee",
      "workflows",
      "display",
      "nodes",
      "types",
    ] as const,
    VELLUM_TYPES_MODULE_PATH: [
      "vellum_ee",
      "workflows",
      "display",
      "vellum",
    ] as const,
    PORTS_MODULE_PATH: [...workflowsSdkModulePath, "ports"] as const,
  };
}
