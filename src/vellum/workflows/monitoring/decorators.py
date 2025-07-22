from uuid import UUID, uuid4
from typing import Any, Callable, Dict, List, Optional

import wrapt

from vellum.workflows.context import get_execution_context
from vellum.workflows.events.types import NodeParentContext, ParentContext, WorkflowParentContext
from vellum.workflows.monitoring.context import (
    MonitoringExecutionContext,
    get_monitoring_execution_context,
    monitoring_execution_context,
)
from vellum.workflows.types.definition import CodeResourceDefinition


class MonitorDecorator:
    """Main decorator for monitoring functions and methods with automatic parent context creation."""

    def __init__(
        self,
        name: Optional[str] = None,
        enabled: bool = True,
        capture_args: bool = True,
        capture_result: bool = True,
        capture_exceptions: bool = True,
    ):
        self.name = name
        self.enabled = enabled
        self.capture_args = capture_args
        self.capture_result = capture_result
        self.capture_exceptions = capture_exceptions

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        if not self.enabled:
            return wrapped(*args, **kwargs)

        # Get current execution and monitoring contexts
        current_exec_context = get_execution_context()
        current_monitoring_context = get_monitoring_execution_context()

        # Determine the name for this monitored call
        monitor_name = self.name or f"{wrapped.__module__}.{wrapped.__qualname__}"

        # Register this method in the registry
        register_monitoring_method(monitor_name)

        # Create appropriate parent context based on inferred context type
        parent_context = self._create_parent_context(
            monitor_name, current_exec_context, current_monitoring_context, instance, wrapped
        )

        # Prepare monitoring data for tracking
        monitoring_data = {
            "name": monitor_name,
            "function": wrapped.__qualname__,
            "module": wrapped.__module__,
            "args": args if self.capture_args else None,
            "kwargs": kwargs if self.capture_args else None,
        }

        try:
            # Only set up monitoring execution context (don't touch main execution context)
            # Check if we already have a monitoring context with a parent
            existing_monitoring_context = get_monitoring_execution_context()
            use_existing_context = (
                existing_monitoring_context.parent_context is not None
                and existing_monitoring_context.trace_id != UUID("00000000-0000-0000-0000-000000000000")
            )

            if use_existing_context:
                # Use existing monitoring context
                # Register this method call within the existing context
                register_monitored_call(monitor_name, monitoring_data)
                result = wrapped(*args, **kwargs)
            else:
                # Create new monitoring context
                with monitoring_execution_context(
                    parent_context=parent_context,
                    trace_id=current_exec_context.trace_id,
                    monitoring_enabled=self.enabled,
                ):
                    # Register this method call within the monitoring context
                    register_monitored_call(monitor_name, monitoring_data)
                    result = wrapped(*args, **kwargs)

            # Capture result if enabled
            if self.capture_result:
                record_monitoring_result(monitor_name, result, None)

            return result

        except Exception as e:
            # Capture exception if enabled
            if self.capture_exceptions:
                record_monitoring_result(monitor_name, None, e)
            raise

    def _create_parent_context(
        self,
        monitor_name: str,
        exec_context: Any,
        monitoring_context: MonitoringExecutionContext,
        instance: Any,
        wrapped: Callable,
    ) -> ParentContext:
        """Create appropriate parent context for the monitored call."""

        # Infer context type from instance
        context_type = self._infer_context_type(instance)

        # Create a code resource definition for this monitored function
        resource_def = CodeResourceDefinition(
            id=uuid4(),
            name=monitor_name,
            module=[wrapped.__module__] if hasattr(wrapped, "__module__") else ["monitoring"],
        )

        # Create appropriate parent context
        if context_type == "WORKFLOW":
            return WorkflowParentContext(
                span_id=uuid4(),
                type="WORKFLOW",
                workflow_definition=resource_def,
                parent=monitoring_context.parent_context or exec_context.parent_context,
            )
        else:
            # Default to NODE context
            return NodeParentContext(
                span_id=uuid4(),
                type="WORKFLOW_NODE",
                node_definition=resource_def,
                parent=monitoring_context.parent_context or exec_context.parent_context,
            )

    def _infer_context_type(self, instance: Any) -> str:
        """Infer the context type from the instance."""
        if instance:
            # Try to infer from instance type
            if hasattr(instance, "__class__"):
                class_name = instance.__class__.__name__
                if "Workflow" in class_name:
                    return "WORKFLOW"
                elif "Node" in class_name:
                    return "NODE"
                else:
                    return "NODE"  # Default to NODE
            else:
                return "NODE"
        else:
            return "NODE"  # Default to NODE


def monitor(
    name: Optional[str] = None,
    enabled: bool = True,
    capture_args: bool = True,
    capture_result: bool = True,
    capture_exceptions: bool = True,
) -> Callable:
    """
    Main decorator for monitoring functions and methods with automatic parent context creation.

    This decorator automatically:
    1. Infers context type from the instance (WORKFLOW or NODE)
    2. Creates appropriate parent context based on the inferred type
    3. Sets up monitoring execution context with the new parent context
    4. Executes the wrapped function
    5. Captures monitoring data

    This replaces manual parent context creation in the runner/nodes.
    Only updates monitoring execution context, not the main execution context.

    Args:
        name: Custom name for this monitored call. If None, uses function qualname.
        enabled: Whether monitoring is enabled for this call.
        capture_args: Whether to capture function arguments.
        capture_result: Whether to capture function return value.
        capture_exceptions: Whether to capture exceptions.

    Example:
        @monitor(name="MyWorkflow.run")
        def run(self, inputs=None, **kwargs):
            # Automatically infers WORKFLOW context type and creates WorkflowParentContext
            return super().run(inputs=inputs, **kwargs)

        @monitor(name="MyNode.process")
        def process(self) -> Outputs:
            # Automatically infers NODE context type and creates NodeParentContext
            return self.Outputs(result=processed_items)
    """
    return MonitorDecorator(
        name=name,
        enabled=enabled,
        capture_args=capture_args,
        capture_result=capture_result,
        capture_exceptions=capture_exceptions,
    )


# Legacy decorators for backward compatibility
def with_monitoring_context(
    parent_context: Optional[ParentContext] = None,
    trace_id: Optional[UUID] = None,
    monitoring_enabled: bool = True,
) -> Callable:
    """Legacy decorator - use @monitor instead."""
    return MonitorDecorator(
        name=None,
        enabled=monitoring_enabled,
        capture_args=False,
        capture_result=False,
        capture_exceptions=False,
    )


def auto_monitoring_context(monitoring_enabled: bool = True) -> Callable:
    """Legacy decorator - use @monitor instead."""
    return MonitorDecorator(
        name=None,
        enabled=monitoring_enabled,
        capture_args=False,
        capture_result=False,
        capture_exceptions=False,
    )


# Registry for tracking monitored methods and calls
_monitoring_registry: Dict[str, Dict[str, Any]] = {}
_monitored_calls: List[Dict[str, Any]] = []


def register_monitoring_method(method_name: str) -> None:
    """Register a method as having monitoring context applied."""
    _monitoring_registry[method_name] = {"registered_at": "now", "decorator_type": "monitor"}  # Could use datetime


def register_monitored_call(name: str, data: Dict[str, Any]) -> None:
    """Register a monitored function call."""
    call_data = {
        "name": name,
        "timestamp": "now",  # Could use datetime
        "data": data,
        "trace_id": get_monitoring_execution_context().trace_id,
    }
    _monitored_calls.append(call_data)


def record_monitoring_result(name: str, result: Any, exception: Optional[Exception]) -> None:
    """Record the result or exception of a monitored call."""
    # Find the most recent call for this name
    for call in reversed(_monitored_calls):
        if call["name"] == name:
            call["result"] = result
            call["exception"] = exception
            call["completed_at"] = "now"  # Could use datetime
            break


def is_monitoring_registered(method_name: str) -> bool:
    """Check if a method is registered for monitoring."""
    return method_name in _monitoring_registry


def get_monitoring_registry() -> Dict[str, Dict[str, Any]]:
    """Get all registered monitoring methods."""
    return _monitoring_registry.copy()


def get_monitored_calls() -> List[Dict[str, Any]]:
    """Get all monitored calls."""
    return _monitored_calls.copy()


def clear_monitoring_registry() -> None:
    """Clear the monitoring registry."""
    _monitoring_registry.clear()
    _monitored_calls.clear()
