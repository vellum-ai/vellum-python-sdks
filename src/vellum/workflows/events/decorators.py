"""Monitoring decorators for workflow tracing."""

import fnmatch
from uuid import UUID, uuid4
from typing import Any, Callable, Optional, cast

import wrapt

from vellum.workflows.context import ExecutionContext
from vellum.workflows.events.context import (
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

        # Get current monitoring context
        current_monitoring = get_monitoring_execution_context()

        # Try to find parent context using the current span_id stored globally
        current_span_id = _monitoring_context_store.get_current_span_id()
        if current_span_id:
            parent_monitoring_context = _monitoring_context_store.retrieve_context_by_span_id(current_span_id)
            if parent_monitoring_context:
                # Use the parent context we found
                current_monitoring = ExecutionContext(
                    trace_id=current_monitoring.trace_id,
                    parent_context=parent_monitoring_context,
                    monitoring_enabled=self.enabled,
                )

        # Get the best trace_id from monitoring system only
        trace_id_to_use = self._get_best_trace_id(current_monitoring)

        # Determine the name for this monitored call
        monitor_name = self.name or f"{wrapped.__module__}.{wrapped.__qualname__}"

        # Create new monitoring parent context for this call
        new_monitoring_parent = self._create_monitoring_parent_context(
            monitor_name, current_monitoring, instance, wrapped
        )

        # Store the new context for potential child calls
        _monitoring_context_store.store_context(trace_id_to_use, new_monitoring_parent)

        # Store the current span_id globally so child methods can find it
        _monitoring_context_store.set_current_span_id(new_monitoring_parent.span_id)

        # Create and set the monitoring context for this execution
        new_monitoring_context = ExecutionContext(
            trace_id=trace_id_to_use,
            parent_context=new_monitoring_parent,
            monitoring_enabled=self.enabled,
        )

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
        """Get the best trace_id from monitoring system only."""
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Priority 1: Use current monitoring context trace_id if not default
        if current_monitoring.trace_id != default_uuid:
            return current_monitoring.trace_id

        # Priority 2: Try global current trace_id from context store
        global_trace_id = _monitoring_context_store.get_current_trace_id()
        if global_trace_id and global_trace_id != default_uuid:
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
            # Convert current monitoring's parent context into the parent for this new context
            # This creates proper nesting: new_method -> current_method -> parent_method
            current_parent = current_monitoring.parent_context
        else:
            # If we have a workflow_class and no current parent, create workflow context as root
            current_parent = None
            if hasattr(self, "workflow_class") and self.workflow_class:
                workflow_resource_def = CodeResourceDefinition(
                    id=uuid4(),
                    name=f"{self.workflow_class.__name__}.run",  # Include the run method name
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
                type="WORKFLOW",
                workflow_definition=resource_def,
                parent=cast(Optional[ParentContext], current_parent),
            )
        else:
            return NodeParentContext(
                span_id=uuid4(),
                type="WORKFLOW_NODE",
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


class SubworkflowMonitoringWrapper(wrapt.ObjectProxy):
    """Wrapper that automatically monitors subworkflow method calls."""

    def __init__(self, wrapped_instance, methods_to_monitor=None, workflow_class=None):
        super().__init__(wrapped_instance)
        self._self_wrapped_instance_name = wrapped_instance.__class__.__name__
        self._self_methods_to_monitor = methods_to_monitor or {"run", "stream"}
        self._self_workflow_class = workflow_class

    def __getattribute__(self, name):
        # Get the attribute normally first
        attr = super().__getattribute__(name)

        # If it's a callable method we want to monitor, wrap it
        if callable(attr) and name in self._self_methods_to_monitor and not hasattr(attr, "__wrapped__"):
            monitor_name = f"{self._self_wrapped_instance_name}.{name}"

            # Subworkflows should appear as NODE context under their containing node
            class SubworkflowNodeDecorator(MonitorDecorator):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Use workflow_class if needed, do not reference _self_workflow_class
                    self.workflow_class = getattr(self, "workflow_class", None)

                def _infer_context_type(self, instance: Any) -> str:
                    return "NODE"

            return SubworkflowNodeDecorator(name=monitor_name)(attr)

        return attr


def wrap_subworkflows_for_monitoring(node_class, methods_to_monitor=None, workflow_class=None):
    """
    Utility function to wrap subworkflows with monitoring for a given node class.

    Args:
        node_class: The node class to scan for subworkflows
        methods_to_monitor: Set of method names to monitor (defaults to {'run', 'stream'})
        workflow_class: Optional workflow class to pass to subworkflows for root parent context
    """
    methods_to_monitor = methods_to_monitor or {"run", "stream"}

    # Instead of wrapping the subworkflow instance, wrap the subworkflow class methods directly
    # This avoids descriptor resolution issues
    for base in node_class.__mro__:
        if hasattr(base, "subworkflow"):
            subworkflow = getattr(base, "subworkflow")
            if subworkflow is not None and hasattr(subworkflow, "__class__"):
                # Wrap the subworkflow class methods directly with WORKFLOW context
                wrap_classes_for_monitoring(
                    [subworkflow.__class__],
                    context_type="WORKFLOW",
                    methods_to_monitor=methods_to_monitor,
                    workflow_class=workflow_class,
                )


def wrap_classes_for_monitoring(classes, context_type="NODE", methods_to_monitor=None, workflow_class=None):
    """
    Utility function to wrap multiple classes with monitoring.

    Args:
        classes: Iterable of classes to wrap
        context_type: Either "WORKFLOW" or "NODE" to determine the monitoring context
        methods_to_monitor: Set of method names to monitor. If None, uses smart detection.
        workflow_class: Optional workflow class to use as root parent context for nodes
    """

    # Create appropriate decorator class
    class ContextMonitorDecorator(MonitorDecorator):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.workflow_class = workflow_class

        def _infer_context_type(self, instance: Any) -> str:
            return context_type

    def get_execution_methods(target_cls) -> set:
        """Smart detection of methods that should be monitored."""
        if methods_to_monitor:
            return methods_to_monitor

        execution_methods = set()

        # Standard execution methods
        standard_methods = {"run", "stream", "execute"}

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
                    monitor_name = f"{cls.__name__}.{method_name}"
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
