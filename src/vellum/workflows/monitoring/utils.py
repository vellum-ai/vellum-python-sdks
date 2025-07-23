import inspect
from typing import Any, Callable, Dict, List, Optional, Set, Type

from vellum.workflows.monitoring.decorators import (
    clear_monitoring_registry,
    get_monitored_calls,
    get_monitoring_registry,
    monitor,
    register_monitoring_method,
)
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.runner.runner import WorkflowRunner
from vellum.workflows.workflows.base import BaseWorkflow


def apply_monitoring_to_class(
    cls: Type,
    method_names: Optional[List[str]] = None,
    monitoring_enabled: bool = True,
) -> Type[Any]:
    """
    Apply monitoring context decorators to methods of a class.

    Args:
        cls: The class to decorate
        method_names: List of method names to decorate. If None, decorates all public methods.
        monitoring_enabled: Whether monitoring is enabled

    Returns:
        The decorated class
    """
    if method_names is None:
        # Get all public methods that don't start with underscore
        method_names = [
            name
            for name, member in inspect.getmembers(cls, inspect.isfunction)
            if not name.startswith("_") and callable(member)
        ]

    for method_name in method_names:
        if hasattr(cls, method_name):
            original_method = getattr(cls, method_name)
            if callable(original_method):
                decorated_method = monitor(
                    name=f"{cls.__name__}.{method_name}",
                    enabled=monitoring_enabled,
                )(original_method)
                setattr(cls, method_name, decorated_method)
                register_monitoring_method(f"{cls.__name__}.{method_name}")

    return cls


def apply_monitoring_to_workflow(
    workflow_class: Type[BaseWorkflow], monitoring_enabled: bool = True
) -> Type[BaseWorkflow]:
    """
    Apply monitoring context to a workflow class.

    Args:
        workflow_class: The workflow class to decorate
        monitoring_enabled: Whether monitoring is enabled

    Returns:
        The decorated workflow class
    """
    # Methods that typically need monitoring context
    workflow_methods = ["run", "stream", "validate"]

    return apply_monitoring_to_class(
        workflow_class,
        method_names=workflow_methods,
        monitoring_enabled=monitoring_enabled,
    )


def apply_monitoring_to_runner(
    runner_class: Type[WorkflowRunner], monitoring_enabled: bool = True
) -> Type[WorkflowRunner]:
    """
    Apply monitoring context to a workflow runner class.

    Args:
        runner_class: The runner class to decorate
        monitoring_enabled: Whether monitoring is enabled

    Returns:
        The decorated runner class
    """
    # Methods that typically need monitoring context
    runner_methods = ["_run_work_item", "_context_run_work_item", "_handle_work_item_event", "_emit_event", "stream"]

    return apply_monitoring_to_class(
        runner_class,
        method_names=runner_methods,
        monitoring_enabled=monitoring_enabled,
    )


def apply_monitoring_to_node(node_class: Type[BaseNode], monitoring_enabled: bool = True) -> Type[BaseNode]:
    """
    Apply monitoring context to a node class.

    Args:
        node_class: The node class to decorate
        monitoring_enabled: Whether monitoring is enabled

    Returns:
        The decorated node class
    """
    # Methods that typically need monitoring context
    node_methods = ["run"]

    return apply_monitoring_to_class(
        node_class,
        method_names=node_methods,
        monitoring_enabled=monitoring_enabled,
    )


def apply_monitoring_to_instance_methods(
    instance: Any,
    method_names: Optional[List[str]] = None,
    monitoring_enabled: bool = True,
) -> Any:
    """
    Apply monitoring context decorators to methods of an instance.

    Args:
        instance: The instance to decorate
        method_names: List of method names to decorate. If None, decorates all public methods.
        monitoring_enabled: Whether monitoring is enabled

    Returns:
        The decorated instance
    """
    if method_names is None:
        # Get all public methods that don't start with underscore
        method_names = [
            name
            for name, member in inspect.getmembers(instance, inspect.ismethod)
            if not name.startswith("_") and callable(member)
        ]

    for method_name in method_names:
        if hasattr(instance, method_name):
            original_method = getattr(instance, method_name)
            if callable(original_method):
                decorated_method = monitor(
                    name=f"{instance.__class__.__name__}.{method_name}",
                    enabled=monitoring_enabled,
                )(original_method)
                setattr(instance, method_name, decorated_method)
                register_monitoring_method(f"{instance.__class__.__name__}.{method_name}")

    return instance


def apply_monitoring_dynamically(
    cls: Type,
    method_names: Optional[List[str]] = None,
) -> Type:
    """
    Dynamically apply monitoring to methods of a class.

    Args:
        cls: The class to apply monitoring to
        method_names: List of method names to monitor. If None, monitors common methods.

    Returns:
        The modified class with monitoring applied
    """
    if method_names is None:
        # Default methods to monitor based on class type
        if hasattr(cls, "__name__"):
            class_name = cls.__name__
            if "Workflow" in class_name:
                method_names = ["run", "stream", "validate"]
            elif "Node" in class_name:
                method_names = ["run"]
            else:
                method_names = ["run"]  # Default
        else:
            method_names = ["run"]

    for method_name in method_names:
        if hasattr(cls, method_name):
            original_method = getattr(cls, method_name)
            if callable(original_method):
                # Apply monitoring decorator
                monitored_method = monitor(name=f"{cls.__name__}.{method_name}")(original_method)
                setattr(cls, method_name, monitored_method)

    return cls


def wrap_method_with_monitoring(
    func: Callable,
    name: Optional[str] = None,
) -> Callable:
    """
    Wrap a single callable with monitoring.

    Args:
        func: The function to wrap
        name: Custom name for monitoring. If None, uses function qualname.

    Returns:
        The wrapped function with monitoring applied
    """
    return monitor(name=name)(func)


def apply_monitoring_to_existing_instance(
    instance: Any,
    method_names: Optional[List[str]] = None,
) -> None:
    """
    Apply monitoring to methods of an existing object instance.

    Args:
        instance: The object instance to apply monitoring to
        method_names: List of method names to monitor. If None, monitors common methods.
    """
    if method_names is None:
        # Default methods to monitor based on instance type
        if hasattr(instance, "__class__"):
            class_name = instance.__class__.__name__
            if "Workflow" in class_name:
                method_names = ["run", "stream", "validate"]
            elif "Node" in class_name:
                method_names = ["run"]
            else:
                method_names = ["run"]  # Default
        else:
            method_names = ["run"]

    for method_name in method_names:
        if hasattr(instance, method_name):
            original_method = getattr(instance, method_name)
            if callable(original_method):
                # Apply monitoring decorator
                monitored_method = monitor(name=f"{instance.__class__.__name__}.{method_name}")(original_method)
                setattr(instance, method_name, monitored_method)


def get_methods_needing_monitoring() -> Dict[str, List[str]]:
    """
    Get a mapping of class names to methods that typically need monitoring context.

    Returns:
        Dictionary mapping class names to lists of method names
    """
    return {
        "BaseWorkflow": ["run", "stream", "validate"],
        "WorkflowRunner": [
            "_run_work_item",
            "_context_run_work_item",
            "_handle_work_item_event",
            "_emit_event",
            "stream",
        ],
        "BaseNode": ["run"],
        "MapNode": ["run", "_context_run_subworkflow", "_run_subworkflow"],
        "InlineSubworkflowNode": ["run"],
        "RetryNode": ["run"],
        "TryNode": ["run"],
        "ToolCallingNode": ["run"],
    }


def auto_apply_monitoring_to_known_classes(monitoring_enabled: bool = True) -> Dict[str, Set[str]]:
    """
    Automatically apply monitoring to known workflow classes.

    Args:
        monitoring_enabled: Whether monitoring is enabled

    Returns:
        Dictionary mapping class names to sets of decorated method names
    """
    methods_needing_monitoring = get_methods_needing_monitoring()
    decorated_methods: Dict[str, Set[str]] = {}

    # Apply to BaseWorkflow
    if "BaseWorkflow" in methods_needing_monitoring:
        apply_monitoring_to_workflow(BaseWorkflow, monitoring_enabled)
        decorated_methods["BaseWorkflow"] = set(methods_needing_monitoring["BaseWorkflow"])

    # Apply to WorkflowRunner
    if "WorkflowRunner" in methods_needing_monitoring:
        apply_monitoring_to_runner(WorkflowRunner, monitoring_enabled)
        decorated_methods["WorkflowRunner"] = set(methods_needing_monitoring["WorkflowRunner"])

    # Apply to BaseNode
    if "BaseNode" in methods_needing_monitoring:
        apply_monitoring_to_node(BaseNode, monitoring_enabled)
        decorated_methods["BaseNode"] = set(methods_needing_monitoring["BaseNode"])

    return decorated_methods


def sync_monitoring_with_execution_context() -> None:
    """
    Ensure monitoring execution context is synchronized with the main execution context.
    This should be called periodically or at key points in the workflow execution.
    """
    from vellum.workflows.context import get_execution_context
    from vellum.workflows.monitoring.context import (
        MonitoringExecutionContext,
        get_monitoring_execution_context,
        set_monitoring_execution_context,
    )

    exec_context = get_execution_context()
    monitoring_context = get_monitoring_execution_context()

    # Sync if they're out of sync
    if (
        exec_context.trace_id != monitoring_context.trace_id
        or exec_context.parent_context != monitoring_context.parent_context
    ):

        new_monitoring_context = MonitoringExecutionContext(
            trace_id=exec_context.trace_id,
            parent_context=exec_context.parent_context,
            monitoring_enabled=monitoring_context.monitoring_enabled,
        )
        set_monitoring_execution_context(new_monitoring_context)


def get_monitoring_summary() -> Dict[str, Any]:
    """
    Get a summary of all monitoring activity.

    Returns:
        Dictionary containing monitoring registry and call history
    """
    return {
        "registry": get_monitoring_registry(),
        "calls": get_monitored_calls(),
        "total_registered_methods": len(get_monitoring_registry()),
        "total_monitored_calls": len(get_monitored_calls()),
    }


def reset_monitoring() -> None:
    """Reset all monitoring state."""
    clear_monitoring_registry()


def enable_monitoring_for_workflow(workflow_class: Type[BaseWorkflow]) -> Type[BaseWorkflow]:
    """
    Enable monitoring for a specific workflow class.
    This is a convenience function for applying monitoring to workflows.

    Args:
        workflow_class: The workflow class to enable monitoring for

    Returns:
        The workflow class with monitoring enabled
    """
    return apply_monitoring_to_workflow(workflow_class, monitoring_enabled=True)


def enable_monitoring_for_node(node_class: Type[BaseNode]) -> Type[BaseNode]:
    """
    Enable monitoring for a specific node class.
    This is a convenience function for applying monitoring to nodes.

    Args:
        node_class: The node class to enable monitoring for

    Returns:
        The node class with monitoring enabled
    """
    return apply_monitoring_to_node(node_class, monitoring_enabled=True)
