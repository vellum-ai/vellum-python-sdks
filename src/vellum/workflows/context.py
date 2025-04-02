from contextlib import contextmanager
from dataclasses import field
import threading
from uuid import UUID
from typing import Iterator, Optional, cast

from vellum.client.core import UniversalBaseModel
from vellum.workflows.events.types import ParentContext


class ExecutionContext(UniversalBaseModel):
    trace_id: UUID = field(default_factory=lambda: UUID("00000000-0000-0000-0000-000000000000"))
    parent_context: Optional[ParentContext] = None


_CONTEXT_KEY = "_execution_context"

local = threading.local()


def get_execution_context() -> ExecutionContext:
    """Retrieve the current execution context."""
    return getattr(local, _CONTEXT_KEY, ExecutionContext())


def set_execution_context(context: ExecutionContext) -> None:
    """Set the current execution context."""
    setattr(local, _CONTEXT_KEY, context)


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
