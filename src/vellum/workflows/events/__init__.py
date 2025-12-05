from vellum._lazy import make_lazy_loader

_LAZY_IMPORTS = {
    "NodeEvent": (".node", "NodeEvent"),
    "NodeExecutionFulfilledEvent": (".node", "NodeExecutionFulfilledEvent"),
    "NodeExecutionInitiatedEvent": (".node", "NodeExecutionInitiatedEvent"),
    "NodeExecutionRejectedEvent": (".node", "NodeExecutionRejectedEvent"),
    "NodeExecutionStreamingEvent": (".node", "NodeExecutionStreamingEvent"),
    "WorkflowEventGenerator": (".stream", "WorkflowEventGenerator"),
    "WorkflowEvent": (".workflow", "WorkflowEvent"),
    "WorkflowEventStream": (".workflow", "WorkflowEventStream"),
    "WorkflowExecutionFulfilledEvent": (".workflow", "WorkflowExecutionFulfilledEvent"),
    "WorkflowExecutionInitiatedEvent": (".workflow", "WorkflowExecutionInitiatedEvent"),
    "WorkflowExecutionRejectedEvent": (".workflow", "WorkflowExecutionRejectedEvent"),
    "WorkflowExecutionStreamingEvent": (".workflow", "WorkflowExecutionStreamingEvent"),
}

__getattr__, __dir__ = make_lazy_loader(__name__, _LAZY_IMPORTS)

__all__ = [
    "NodeExecutionFulfilledEvent",
    "WorkflowExecutionFulfilledEvent",
    "NodeExecutionInitiatedEvent",
    "WorkflowExecutionInitiatedEvent",
    "NodeEvent",
    "NodeExecutionRejectedEvent",
    "WorkflowExecutionRejectedEvent",
    "NodeExecutionStreamingEvent",
    "WorkflowExecutionStreamingEvent",
    "WorkflowEvent",
    "WorkflowEventStream",
    "WorkflowEventGenerator",
]
