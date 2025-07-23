"""Monitoring decorators for workflow tracing."""

import fnmatch
from uuid import UUID, uuid4
from typing import Any, Callable, Optional

import wrapt

from vellum.workflows.context import get_execution_context
from vellum.workflows.events.types import NodeParentContext, ParentContext, WorkflowParentContext
from vellum.workflows.monitoring.context import (
    MonitoringExecutionContext,
    _monitoring_context_store,
    get_monitoring_execution_context,
    set_monitoring_execution_context,
)
from vellum.workflows.types.definition import CodeResourceDefinition


class MonitorDecorator:
    """Self-sufficient monitoring decorator using wrapt."""

    def __init__(
        self,
        name: Optional[str] = None,
        enabled: bool = True,
        capture_exceptions: bool = True,
    ):
        self.name = name
        self.enabled = enabled
        self.capture_exceptions = capture_exceptions

    def __call__(self, wrapped):
        """Apply the decorator using wrapt.decorator."""
        return self._monitor_decorator(wrapped)

    @wrapt.decorator
    def _monitor_decorator(self, wrapped, instance, args, kwargs):
        """Self-sufficient monitoring decorator that handles everything automatically."""
        if not self.enabled:
            return wrapped(*args, **kwargs)

        # Get current execution context
        current_exec_context = get_execution_context()

        # Determine trace_id to use - prefer execution context, fall back to stored trace_id
        trace_id_to_use = self._get_best_trace_id(current_exec_context)

        # Get or create monitoring context for this call
        monitoring_context = self._get_or_create_monitoring_context(trace_id_to_use, current_exec_context)

        # Determine the name for this monitored call
        monitor_name = self.name or f"{wrapped.__module__}.{wrapped.__qualname__}"

        # Create new monitoring parent context for this call
        new_monitoring_parent = self._create_monitoring_parent_context(
            monitor_name, monitoring_context, instance, wrapped
        )

        # Store the new context for potential child calls
        _monitoring_context_store.store_context(trace_id_to_use, new_monitoring_parent)

        # Create and set the monitoring context for this execution
        new_monitoring_context = MonitoringExecutionContext(
            trace_id=trace_id_to_use,
            parent_context=new_monitoring_parent,
            monitoring_enabled=self.enabled,
        )

        # Save previous context and set new one
        prev_monitoring_context = get_monitoring_execution_context()
        set_monitoring_execution_context(new_monitoring_context)

        try:
            result = wrapped(*args, **kwargs)
            return result
        except Exception:
            if self.capture_exceptions:
                # For now, just re-raise - full implementation would capture the exception
                pass
            raise
        finally:
            # Restore previous monitoring context
            set_monitoring_execution_context(prev_monitoring_context)

    def _get_best_trace_id(self, exec_context: Any) -> UUID:
        """Get the best trace_id, avoiding default UUIDs when possible."""
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Priority 1: Use execution context if it has proper trace_id
        if exec_context.trace_id != default_uuid:
            return exec_context.trace_id

        # Priority 2: Use current monitoring context trace_id if not default
        current_monitoring = get_monitoring_execution_context()
        if current_monitoring.trace_id != default_uuid:
            return current_monitoring.trace_id

        # Priority 3: Try global current trace_id from context store
        global_trace_id = _monitoring_context_store.get_current_trace_id()
        if global_trace_id and global_trace_id != default_uuid:
            return global_trace_id

        # Priority 4: Generate new UUID as last resort
        return uuid4()

    def _get_or_create_monitoring_context(self, trace_id: UUID, exec_context: Any) -> MonitoringExecutionContext:
        """Get existing monitoring context or create one."""
        # Try to get current monitoring context
        current_monitoring = get_monitoring_execution_context()

        # If we have a valid monitoring context with same trace_id, use it
        if current_monitoring.parent_context is not None and current_monitoring.trace_id == trace_id:
            return current_monitoring

        # Try to retrieve stored monitoring context
        stored_parent = _monitoring_context_store.retrieve_context(trace_id, exec_context.parent_context)

        if stored_parent:
            # Found stored context - create monitoring context from it
            return MonitoringExecutionContext(trace_id=trace_id, parent_context=stored_parent, monitoring_enabled=True)

        # No stored context - create from execution context if available
        if exec_context.parent_context:
            return MonitoringExecutionContext(
                trace_id=trace_id, parent_context=exec_context.parent_context, monitoring_enabled=True
            )

        # Default fallback
        return MonitoringExecutionContext(trace_id=trace_id, parent_context=None, monitoring_enabled=True)

    def _create_monitoring_parent_context(
        self,
        monitor_name: str,
        monitoring_context: MonitoringExecutionContext,
        instance: Any,
        wrapped: Callable,
    ) -> ParentContext:
        """Create new monitoring parent context for this call."""
        # Current monitoring parent becomes parent of this new context
        current_parent = monitoring_context.parent_context

        # Infer context type from instance
        context_type = self._infer_context_type(instance)

        # Create monitoring-specific resource definition
        resource_def = CodeResourceDefinition(
            id=uuid4(),
            name=monitor_name,
            module=[wrapped.__module__] if hasattr(wrapped, "__module__") else ["monitoring"],
        )

        # Create the new parent context layer
        if context_type == "WORKFLOW":
            return WorkflowParentContext(
                span_id=uuid4(),
                type="WORKFLOW",
                workflow_definition=resource_def,
                parent=current_parent,
            )
        else:
            return NodeParentContext(
                span_id=uuid4(),
                type="WORKFLOW_NODE",
                node_definition=resource_def,
                parent=current_parent,
            )

    def _infer_context_type(self, instance: Any) -> str:
        """Infer whether this is a workflow or node context."""
        if instance is None:
            return "NODE"

        instance_class_name = instance.__class__.__name__
        instance_module = getattr(instance.__class__, "__module__", "")

        # Workflow patterns
        workflow_patterns = ["*Workflow*", "*workflow*", "*.workflows.*", "*BaseWorkflow*"]

        for pattern in workflow_patterns:
            if fnmatch.fnmatch(instance_class_name, pattern) or fnmatch.fnmatch(instance_module, pattern):
                return "WORKFLOW"

        return "NODE"


def monitor(
    name: Optional[str] = None,
    enabled: bool = True,
    capture_exceptions: bool = True,
) -> Callable:
    """
    Self-sufficient monitoring decorator.

    Works completely independently with just wrapt:
    - No external context managers needed
    - Handles thread boundaries automatically
    - Builds progressive monitoring hierarchy

    Usage:
        @monitor(name="my_function")
        def my_function():
            pass

        class MyNode(BaseNode):
            @monitor()
            def run(self):
                pass
    """
    return MonitorDecorator(
        name=name,
        enabled=enabled,
        capture_exceptions=capture_exceptions,
    )
