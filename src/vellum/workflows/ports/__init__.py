from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "NodePorts": (".node_ports", "NodePorts"),
    "Port": (".port", "Port"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "NodePorts",
    "Port",
]
