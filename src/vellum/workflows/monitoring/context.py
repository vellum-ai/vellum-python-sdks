from contextlib import contextmanager
from dataclasses import field
import threading
from uuid import UUID
from typing import Iterator, Optional, cast

from vellum.client.core import UniversalBaseModel
from vellum.workflows.context import get_execution_context
from vellum.workflows.events.types import ParentContext


class MonitoringExecutionContext(UniversalBaseModel):
    """Monitoring-specific execution context that runs in parallel with ExecutionContext."""

    trace_id: UUID = field(default_factory=lambda: UUID("00000000-0000-0000-0000-000000000000"))
    parent_context: Optional[ParentContext] = None
    monitoring_enabled: bool = True


_MONITORING_CONTEXT_KEY = "_monitoring_execution_context"

monitoring_local = threading.local()


def get_monitoring_execution_context() -> MonitoringExecutionContext:
    """Retrieve the current monitoring execution context."""
    return getattr(monitoring_local, _MONITORING_CONTEXT_KEY, MonitoringExecutionContext())


def set_monitoring_execution_context(context: MonitoringExecutionContext) -> None:
    """Set the current monitoring execution context."""
    setattr(monitoring_local, _MONITORING_CONTEXT_KEY, context)


def get_monitoring_parent_context() -> ParentContext:
    """Get the parent context from monitoring execution context."""
    return cast(ParentContext, get_monitoring_execution_context().parent_context)


@contextmanager
def monitoring_execution_context(
    parent_context: Optional[ParentContext] = None, trace_id: Optional[UUID] = None, monitoring_enabled: bool = True
) -> Iterator[None]:
    """Context manager for handling monitoring execution context."""
    prev_context = get_monitoring_execution_context()

    # Get current execution context to inherit trace_id if not provided
    current_exec_context = get_execution_context()

    # Prioritize provided trace_id, then execution context,
    # then current monitoring context (if not default), then default
    default_uuid = UUID("00000000-0000-0000-0000-000000000000")
    prev_trace_id = prev_context.trace_id if prev_context.trace_id != default_uuid else None

    set_trace_id = trace_id or prev_trace_id or current_exec_context.trace_id or default_uuid
    set_parent_context = parent_context or prev_context.parent_context

    set_context = MonitoringExecutionContext(
        parent_context=set_parent_context, trace_id=set_trace_id, monitoring_enabled=monitoring_enabled
    )
    try:
        set_monitoring_execution_context(set_context)
        yield
    finally:
        set_monitoring_execution_context(prev_context)
