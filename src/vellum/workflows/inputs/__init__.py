from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "BaseInputs": (".base", "BaseInputs"),
    "DatasetRow": (".dataset_row", "DatasetRow"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "BaseInputs",
    "DatasetRow",
]
