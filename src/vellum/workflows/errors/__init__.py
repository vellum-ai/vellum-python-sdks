from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "WorkflowError": (".types", "WorkflowError"),
    "WorkflowErrorCode": (".types", "WorkflowErrorCode"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "WorkflowError",
    "WorkflowErrorCode",
]
