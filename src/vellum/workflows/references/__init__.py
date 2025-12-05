from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "EnvironmentVariableReference": (".environment_variable", "EnvironmentVariableReference"),
    "ExternalInputReference": (".external_input", "ExternalInputReference"),
    "LazyReference": (".lazy", "LazyReference"),
    "NodeReference": (".node", "NodeReference"),
    "OutputReference": (".output", "OutputReference"),
    "StateValueReference": (".state_value", "StateValueReference"),
    "TriggerAttributeReference": (".trigger", "TriggerAttributeReference"),
    "VellumSecretReference": (".vellum_secret", "VellumSecretReference"),
    "WorkflowInputReference": (".workflow_input", "WorkflowInputReference"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "EnvironmentVariableReference",
    "ExternalInputReference",
    "LazyReference",
    "NodeReference",
    "OutputReference",
    "StateValueReference",
    "TriggerAttributeReference",
    "VellumSecretReference",
    "WorkflowInputReference",
]
