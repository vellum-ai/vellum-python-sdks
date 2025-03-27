/* Module paths */
export const VELLUM_CLIENT_MODULE_PATH = ["vellum"] as const;
export const VELLUM_WORKFLOW_NODE_BASE_TYPES_PATH = [
  "vellum",
  "workflows",
  "nodes",
  "displayable",
  "bases",
  "types",
] as const;
export const VELLUM_WORKFLOW_GRAPH_MODULE_PATH = [
  "vellum",
  "workflows",
  "graph",
] as const;
export const VELLUM_WORKFLOW_NODES_MODULE_PATH = [
  "vellum",
  "workflows",
  "nodes",
] as const;
export const VELLUM_WORKFLOW_CONSTANTS_PATH = [
  "vellum",
  "workflows",
  "references",
  "constant",
] as const;
export const VELLUM_WORKFLOWS_DISPLAY_BASE_PATH = [
  "vellum_ee",
  "workflows",
  "display",
  "base",
] as const;
export const VELLUM_WORKFLOW_EDITOR_TYPES_PATH = [
  "vellum_ee",
  "workflows",
  "display",
  "editor",
] as const;
/* Class names */
export const OUTPUTS_CLASS_NAME = "Outputs";
export const PORTS_CLASS_NAME = "Ports";
export const DEFAULT_PORT_NAME = "default";

/* File names */
export const INIT_FILE_NAME = "__init__.py";

export const GENERATED_WORKFLOW_MODULE_NAME = "workflow";

export const GENERATED_INPUTS_MODULE_NAME = "inputs";

export const GENERATED_NODES_MODULE_NAME = "nodes";

export const GENERATED_DISPLAY_MODULE_NAME = "display";
export const GENERATED_NODES_PATH = [GENERATED_NODES_MODULE_NAME] as const;

export const GENERATED_DISPLAY_NODE_MODULE_PATH = [
  GENERATED_DISPLAY_MODULE_NAME,
  GENERATED_NODES_MODULE_NAME,
] as const;

export const GENERATED_NESTED_NODE_MODULE_NAME = "node";
