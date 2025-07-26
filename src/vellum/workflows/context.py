from contextlib import contextmanager
from dataclasses import field
import threading
from uuid import UUID
from typing import Iterator, Optional, cast

from vellum.client.core import UniversalBaseModel
from vellum.workflows.events.context import DEFAULT_TRACE_ID, MonitoringContextStore
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
    if context.trace_id != DEFAULT_TRACE_ID or context.parent_context:
        return context

    # If no thread-local context, try to restore from global store using current trace_id
    trace_id = monitoring_context_store.get_current_trace_id()
    span_id = monitoring_context_store.get_current_span_id()
    if trace_id and trace_id != DEFAULT_TRACE_ID:
        context = monitoring_context_store.retrieve_context(trace_id, span_id)
        if context and (context.parent_context or context.trace_id != DEFAULT_TRACE_ID):
            set_execution_context(context)
            return context
    return ExecutionContext()


def set_execution_context(context: ExecutionContext) -> None:
    """Set the current monitoring execution context and persist it for cross-boundary access."""
    setattr(local, _CONTEXT_KEY, context)

    # Always store in global store for cross-thread access
    monitoring_context_store.store_context(context)
    
    # Set current trace and span IDs for this thread
    if context.trace_id and context.trace_id != DEFAULT_TRACE_ID:
        monitoring_context_store.set_current_trace_id(context.trace_id)
    if context.parent_context:
        monitoring_context_store.set_current_span_id(context.parent_context.span_id)


def get_parent_context() -> ParentContext:
    return cast(ParentContext, get_execution_context().parent_context)


@contextmanager
def execution_context(
    parent_context: Optional[ParentContext] = None, trace_id: Optional[UUID] = None
) -> Iterator[None]:
    """Context manager for handling execution context."""
    prev_context = get_execution_context()
    set_trace_id = (
        prev_context.trace_id
        if int(prev_context.trace_id)
        else trace_id or UUID("00000000-0000-0000-0000-000000000000")
    )
    set_parent_context = parent_context or prev_context.parent_context
    set_context = ExecutionContext(parent_context=set_parent_context, trace_id=set_trace_id)
    try:
        set_execution_context(set_context)
        yield
    finally:
        set_execution_context(prev_context)
