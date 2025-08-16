from contextlib import contextmanager
from dataclasses import field
import threading
from uuid import UUID, uuid4
from typing import Iterator, Optional, cast

from vellum.client.core import UniversalBaseModel
from vellum.workflows.events.context import MonitoringContextStore
from vellum.workflows.events.types import ParentContext


class ExecutionContext(UniversalBaseModel):
    trace_id: UUID = field(default_factory=lambda: UUID("00000000-0000-0000-0000-000000000000"))
    parent_context: Optional[ParentContext] = None


_CONTEXT_KEY = "_execution_context"

local = threading.local()

monitoring_context_store = MonitoringContextStore()


def get_execution_context() -> ExecutionContext:
    """Get the current monitoring execution context, with intelligent fallback."""
    context = getattr(local, _CONTEXT_KEY, ExecutionContext())
    if context.parent_context:
        return context

    # If no thread-local context, try to restore from global store using current trace_id
    context = monitoring_context_store.retrieve_context()
    if context and context.parent_context:
        set_execution_context(context)
        return context
    return ExecutionContext()


def set_execution_context(context: ExecutionContext) -> None:
    """Set the current monitoring execution context and persist it for cross-boundary access."""
    setattr(local, _CONTEXT_KEY, context)

    # Always store in global store for cross-thread access
    monitoring_context_store.store_context(context)


def clear_execution_context() -> None:
    """Clear the current monitoring execution context."""
    if hasattr(local, _CONTEXT_KEY):
        delattr(local, _CONTEXT_KEY)
    monitoring_context_store.clear_context()


def get_parent_context() -> ParentContext:
    return cast(ParentContext, get_execution_context().parent_context)


@contextmanager
def execution_context(
    parent_context: Optional[ParentContext] = None, trace_id: Optional[UUID] = None
) -> Iterator[None]:
    """Context manager for handling execution context."""
    prev_context = get_execution_context()
    set_trace_id = prev_context.trace_id if int(prev_context.trace_id) else trace_id or uuid4()
    set_parent_context = parent_context or prev_context.parent_context
    set_context = ExecutionContext(parent_context=set_parent_context, trace_id=set_trace_id)
    try:
        set_execution_context(set_context)
        yield
    finally:
        set_execution_context(prev_context)
