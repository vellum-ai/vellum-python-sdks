"""Monitoring decorators for workflow tracing."""

import fnmatch
from uuid import UUID, uuid4
from typing import Any, Callable, Optional, cast

import wrapt

from vellum.workflows.context import ExecutionContext
from vellum.workflows.events.context import (
    DEFAULT_TRACE_ID,
    _monitoring_context_store,
    get_monitoring_execution_context,
    set_monitoring_execution_context,
)
from vellum.workflows.events.types import NodeParentContext, ParentContext, WorkflowParentContext
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
        """Self-sufficient monitoring decorator using only the new monitoring system."""

        if not self.enabled:
            return wrapped(*args, **kwargs)

        # Get current monitoring context, either from monitoring context store  or our monitoring context
        current_monitoring = get_monitoring_execution_context()

        # Get the best trace_id from monitoring system only
        trace_id_to_use = self._get_best_trace_id(current_monitoring)

        # Determine the name for this monitored call
        monitor_name = self.name or f"{wrapped.__module__}.{wrapped.__qualname__}"

        # Create new monitoring parent context for this call
        new_monitoring_parent = self._create_monitoring_parent_context(
            monitor_name, current_monitoring, instance, wrapped
        )

        # Create and set the monitoring context for this execution
        new_monitoring_context = ExecutionContext(
            trace_id=trace_id_to_use,
            parent_context=new_monitoring_parent,
        )

        # Store the new context for potential child calls
        _monitoring_context_store.store_context(new_monitoring_context)

        # Store the current span_id globally so child methods can find it
        _monitoring_context_store.set_current_span_id(new_monitoring_parent.span_id)

        # Save previous context and set new one
        prev_monitoring_context = current_monitoring
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
            # Restore previous span_id
            prev_span_id = (
                getattr(prev_monitoring_context.parent_context, "span_id", None)
                if prev_monitoring_context.parent_context
                else None
            )
            if prev_span_id:
                _monitoring_context_store.set_current_span_id(prev_span_id)

    def _get_best_trace_id(self, current_monitoring: ExecutionContext) -> UUID:
        # Priority 1: Use current monitoring context trace_id if not default
        if current_monitoring.trace_id != DEFAULT_TRACE_ID:
            return current_monitoring.trace_id

        # Priority 2: Try global current trace_id from context store
        global_trace_id = _monitoring_context_store.get_current_trace_id()
        if global_trace_id and global_trace_id != DEFAULT_TRACE_ID:
            return global_trace_id

        # Priority 3: Generate new UUID and store it globally for this execution
        new_trace_id = uuid4()
        _monitoring_context_store.set_current_trace_id(new_trace_id)
        return new_trace_id

    def _create_monitoring_parent_context(
        self,
        monitor_name: str,
        current_monitoring: ExecutionContext,
        instance: Any,
        wrapped: Callable,
    ) -> ParentContext:
        """Create new monitoring parent context for this call."""
        # Use current monitoring context as parent if it has one
        if current_monitoring.parent_context:
            current_parent = current_monitoring.parent_context
        else:
            # If we have a workflow_class and no current parent, create workflow context as root
            current_parent = None
            if hasattr(self, "workflow_class") and self.workflow_class:
                workflow_resource_def = CodeResourceDefinition(
                    id=uuid4(),
                    name=f"{self.workflow_class.__name__}",
                    module=(
                        [self.workflow_class.__module__]
                        if hasattr(self.workflow_class, "__module__")
                        else ["workflows"]
                    ),
                )
                current_parent = WorkflowParentContext(
                    span_id=uuid4(),
                    type="WORKFLOW",
                    workflow_definition=workflow_resource_def,
                    parent=None,
                )

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
                workflow_definition=resource_def,
                parent=cast(Optional[ParentContext], current_parent),
            )
        else:
            return NodeParentContext(
                span_id=uuid4(),
                node_definition=resource_def,
                parent=cast(Optional[ParentContext], current_parent),
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


def wrap_classes_for_monitoring(classes, parent_context_type="NODE", methods_to_monitor=None, workflow_class=None):
    """
    Utility function to wrap multiple classes with monitoring.

    Args:
        classes: Iterable of classes to wrap
        parent_context_type: Either "WORKFLOW" or "NODE" to determine the monitoring context
        methods_to_monitor: Set of method names to monitor. If None, uses smart detection.
        workflow_class: Optional workflow class to use as root parent context for nodes
    """

    # Create appropriate decorator class
    class ContextMonitorDecorator(MonitorDecorator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.workflow_class = workflow_class

        def _infer_context_type(self, instance: Any) -> str:
            return parent_context_type

    def get_execution_methods(target_cls) -> set:
        """Smart detection of methods that should be monitored."""
        if methods_to_monitor:
            return methods_to_monitor

        execution_methods = set()

        # Standard execution methods
        standard_methods = {"run", "stream"}

        # Check standard methods
        for method_name in standard_methods:
            if hasattr(target_cls, method_name):
                method = getattr(target_cls, method_name)
                if callable(method) and not method_name.startswith("__"):
                    execution_methods.add(method_name)

        return execution_methods

    # Wrap each class
    for cls in classes:
        methods = get_execution_methods(cls)
        for method_name in methods:
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                if callable(method) and not hasattr(method, "__wrapped__"):
                    monitor_name = f"{cls.__name__}"
                    decorator = ContextMonitorDecorator(name=monitor_name)
                    wrapped_method = decorator(method)
                    setattr(cls, method_name, wrapped_method)


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
