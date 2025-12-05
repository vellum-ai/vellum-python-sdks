from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    # Base
    "BaseNode": (".bases", "BaseNode"),
    # Core
    "ErrorNode": (".core", "ErrorNode"),
    "InlineSubworkflowNode": (".core", "InlineSubworkflowNode"),
    "MapNode": (".core", "MapNode"),
    "RetryNode": (".core", "RetryNode"),
    "TemplatingNode": (".core", "TemplatingNode"),
    "TryNode": (".core", "TryNode"),
    # Displayable Base Nodes
    "BaseInlinePromptNode": (".displayable.bases", "BaseInlinePromptNode"),
    "BasePromptDeploymentNode": (".displayable.bases", "BasePromptDeploymentNode"),
    "BaseSearchNode": (".displayable.bases", "BaseSearchNode"),
    # Displayable Nodes
    "APINode": (".displayable", "APINode"),
    "CodeExecutionNode": (".displayable", "CodeExecutionNode"),
    "ConditionalNode": (".displayable", "ConditionalNode"),
    "FinalOutputNode": (".displayable", "FinalOutputNode"),
    "GuardrailNode": (".displayable", "GuardrailNode"),
    "InlinePromptNode": (".displayable", "InlinePromptNode"),
    "NoteNode": (".displayable", "NoteNode"),
    "PromptDeploymentNode": (".displayable", "PromptDeploymentNode"),
    "SearchNode": (".displayable", "SearchNode"),
    "SubworkflowDeploymentNode": (".displayable", "SubworkflowDeploymentNode"),
    "WebSearchNode": (".displayable", "WebSearchNode"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    # Base
    "BaseNode",
    # Core
    "ErrorNode",
    "InlineSubworkflowNode",
    "MapNode",
    "RetryNode",
    "TemplatingNode",
    "TryNode",
    # Displayable Base Nodes
    "BaseInlinePromptNode",
    "BasePromptDeploymentNode",
    "BaseSearchNode",
    # Displayable Nodes
    "APINode",
    "CodeExecutionNode",
    "ConditionalNode",
    "FinalOutputNode",
    "GuardrailNode",
    "InlinePromptNode",
    "NoteNode",
    "PromptDeploymentNode",
    "SearchNode",
    "SubworkflowDeploymentNode",
    "WebSearchNode",
]
