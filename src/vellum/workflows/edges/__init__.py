from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "Edge": (".edge", "Edge"),
    "TriggerEdge": (".trigger_edge", "TriggerEdge"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "Edge",
    "TriggerEdge",
]
