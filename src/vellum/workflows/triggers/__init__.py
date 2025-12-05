from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "BaseTrigger": (".base", "BaseTrigger"),
    "IntegrationTrigger": (".integration", "IntegrationTrigger"),
    "ManualTrigger": (".manual", "ManualTrigger"),
    "ScheduleTrigger": (".schedule", "ScheduleTrigger"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = ["BaseTrigger", "IntegrationTrigger", "ManualTrigger", "ScheduleTrigger"]
