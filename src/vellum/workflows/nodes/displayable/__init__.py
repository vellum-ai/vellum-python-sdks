from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "ErrorNode": ("..core.error_node", "ErrorNode"),
    "InlineSubworkflowNode": ("..core.inline_subworkflow_node", "InlineSubworkflowNode"),
    "MapNode": ("..core.map_node", "MapNode"),
    "TemplatingNode": ("..core.templating_node", "TemplatingNode"),
    "APINode": (".api_node", "APINode"),
    "CodeExecutionNode": (".code_execution_node", "CodeExecutionNode"),
    "ConditionalNode": (".conditional_node", "ConditionalNode"),
    "FinalOutputNode": (".final_output_node", "FinalOutputNode"),
    "GuardrailNode": (".guardrail_node", "GuardrailNode"),
    "InlinePromptNode": (".inline_prompt_node", "InlinePromptNode"),
    "MergeNode": (".merge_node", "MergeNode"),
    "NoteNode": (".note_node", "NoteNode"),
    "PromptDeploymentNode": (".prompt_deployment_node", "PromptDeploymentNode"),
    "SearchNode": (".search_node", "SearchNode"),
    "SetStateNode": (".set_state_node", "SetStateNode"),
    "SubworkflowDeploymentNode": (".subworkflow_deployment_node", "SubworkflowDeploymentNode"),
    "ToolCallingNode": (".tool_calling_node", "ToolCallingNode"),
    "WebSearchNode": (".web_search_node", "WebSearchNode"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "APINode",
    "CodeExecutionNode",
    "ConditionalNode",
    "ErrorNode",
    "InlinePromptNode",
    "InlineSubworkflowNode",
    "GuardrailNode",
    "MapNode",
    "MergeNode",
    "NoteNode",
    "SubworkflowDeploymentNode",
    "PromptDeploymentNode",
    "SearchNode",
    "SetStateNode",
    "TemplatingNode",
    "ToolCallingNode",
    "WebSearchNode",
    "FinalOutputNode",
]
