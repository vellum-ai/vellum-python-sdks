/**
 * Mapping of base node class names to their default Display icon and color values.
 * These defaults are defined in the Python SDK in each node's Display class.
 *
 * This mapping is used by the codegen to skip generating icon/color fields in nested
 * Display classes when they match the base class defaults, keeping generated code lean.
 */
export const BASE_NODE_DISPLAY_DEFAULTS: Record<
  string,
  { icon?: string; color?: string }
> = {
  // From src/vellum/workflows/nodes/displayable/api_node/node.py
  BaseAPINode: {
    icon: "vellum:icon:signal-stream",
    color: "lightBlue",
  },
  // From src/vellum/workflows/nodes/displayable/search_node/node.py
  BaseSearchNode: {
    icon: "vellum:icon:magnifying-glass-waveform",
    color: "purple",
  },
  // From src/vellum/workflows/nodes/displayable/inline_prompt_node/node.py
  BaseInlinePromptNode: {
    icon: "vellum:icon:text-size",
    color: "navy",
  },
  // From src/vellum/workflows/nodes/displayable/prompt_deployment_node/node.py
  BasePromptDeploymentNode: {
    icon: "vellum:icon:text-size",
    color: "navy",
  },
  // From src/vellum/workflows/nodes/displayable/guardrail_node/node.py
  GuardrailNode: {
    icon: "vellum:icon:shield-check",
    color: "rose",
  },
  // From src/vellum/workflows/nodes/displayable/search_node/node.py
  SearchNode: {
    icon: "vellum:icon:magnifying-glass-waveform",
    color: "purple",
  },
  // From src/vellum/workflows/nodes/displayable/tool_calling_node/node.py
  ToolCallingNode: {
    icon: "vellum:icon:wrench",
    color: "teal",
  },
  // From src/vellum/workflows/nodes/displayable/inline_prompt_node/node.py
  InlinePromptNode: {
    icon: "vellum:icon:text-size",
    color: "navy",
  },
  // From src/vellum/workflows/nodes/displayable/conditional_node/node.py
  ConditionalNode: {
    icon: "vellum:icon:split",
    color: "corn",
  },
  // From src/vellum/workflows/nodes/displayable/code_execution_node/node.py
  CodeExecutionNode: {
    icon: "vellum:icon:rectangle-code",
    color: "lime",
  },
  // From src/vellum/workflows/nodes/displayable/final_output_node/node.py
  FinalOutputNode: {
    icon: "vellum:icon:circle-stop",
    color: "teal",
  },
  // From src/vellum/workflows/nodes/displayable/api_node/node.py
  APINode: {
    icon: "vellum:icon:signal-stream",
    color: "lightBlue",
  },
  // From src/vellum/workflows/nodes/displayable/note_node/node.py
  NoteNode: {
    icon: "vellum:icon:note",
    color: "cyan",
  },
  // From src/vellum/workflows/nodes/displayable/merge_node/node.py
  MergeNode: {
    icon: "vellum:icon:merge",
    color: "tomato",
  },
  // From src/vellum/workflows/nodes/displayable/subworkflow_deployment_node/node.py
  SubworkflowDeploymentNode: {
    icon: "vellum:icon:diagram-sankey",
    color: "grass",
  },
  // From src/vellum/workflows/nodes/displayable/prompt_deployment_node/node.py
  PromptDeploymentNode: {
    icon: "vellum:icon:text-size",
    color: "navy",
  },
  // From src/vellum/workflows/nodes/displayable/web_search_node/node.py
  WebSearchNode: {
    icon: "vellum:icon:magnifying-glass",
    color: "lightBlue",
  },
  // BaseNode has no default icon/color (both are None)
  BaseNode: {},
};
