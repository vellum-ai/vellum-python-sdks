from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "BaseInlinePromptNode": (".node", "BaseInlinePromptNode"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "BaseInlinePromptNode",
]
