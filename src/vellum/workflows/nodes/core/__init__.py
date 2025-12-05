from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "BaseAPINode": ("vellum.workflows.nodes.displayable.bases.api_node", "BaseAPINode"),
    "ErrorNode": (".error_node", "ErrorNode"),
    "InlineSubworkflowNode": (".inline_subworkflow_node", "InlineSubworkflowNode"),
    "MapNode": (".map_node", "MapNode"),
    "RetryNode": (".retry_node", "RetryNode"),
    "TemplatingNode": (".templating_node", "TemplatingNode"),
    "TryNode": (".try_node", "TryNode"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "BaseAPINode",
    "ErrorNode",
    "InlineSubworkflowNode",
    "MapNode",
    "RetryNode",
    "TemplatingNode",
    "TryNode",
]
