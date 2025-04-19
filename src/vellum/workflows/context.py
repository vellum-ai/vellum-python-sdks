from contextlib import contextmanager
from dataclasses import field
import threading
from uuid import UUID, uuid4
from typing import Iterator, Optional

from vellum.client.core import UniversalBaseModel
from vellum.workflows.events.types import ParentContext


def _uuid4_factory() -> UUID:
    """
    A factory function for generating UUIDs. Used to help with testing.
    """

    return uuid4()


class ExecutionContext(UniversalBaseModel):
    trace_id: UUID = field(default_factory=_uuid4_factory)
    parent_context: Optional[ParentContext] = None


_CONTEXT_KEY = "_execution_context"

local = threading.local()


def get_execution_context() -> Optional[ExecutionContext]:
    """Retrieve the current execution context."""
    return getattr(local, _CONTEXT_KEY, None)


def set_execution_context(context: Optional[ExecutionContext] = None) -> None:
    """Set the current execution context."""
    setattr(local, _CONTEXT_KEY, context)


def get_parent_context() -> Optional[ParentContext]:
    execution_context = get_execution_context()
    if execution_context is None:
        return None
    return execution_context.parent_context


@contextmanager
def execution_context(parent_context: Optional[ParentContext] = None) -> Iterator[None]:
    """Context manager for handling execution context."""
    prev_context = get_execution_context()
    if prev_context:
        set_context = ExecutionContext(
            parent_context=parent_context or prev_context.parent_context, trace_id=prev_context.trace_id
        )
    else:
        set_context = ExecutionContext(parent_context=parent_context)
    try:
        set_execution_context(set_context)
        yield
    finally:
        set_execution_context(prev_context)
