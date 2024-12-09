from contextlib import contextmanager
import threading
from typing import Any, Callable, Dict, Iterator, TypeVar, cast

from vellum.workflows.events.types import ParentContext

ExecutionLocalContext = Dict[str, Any]
_CONTEXT_KEY = "_execution_context"

local = threading.local()

_context_lock = threading.Lock()

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")
P = TypeVar("P", bound=ParentContext)


def get_execution_context() -> ExecutionLocalContext:
    """Retrieve the current execution context."""
    return getattr(local, _CONTEXT_KEY, {})


def set_execution_context(context: ExecutionLocalContext) -> None:
    """Set the current execution context."""
    setattr(local, _CONTEXT_KEY, context)


def get_parent_context() -> ParentContext:
    return cast(ParentContext, get_execution_context().get("parent_context"))


@contextmanager
def execution_context(**kwargs: Any) -> Iterator[None]:
    """Context manager for handling execution context."""
    prev_context = get_execution_context()
    new_context = {**prev_context, **kwargs}
    try:
        set_execution_context(new_context)
        yield
    finally:
        set_execution_context(prev_context)
