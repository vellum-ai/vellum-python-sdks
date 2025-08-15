import threading
from uuid import UUID
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from vellum.workflows.context import ExecutionContext


class RelationalThread(threading.Thread):
    _parent_thread: Optional[int] = None
    _trace_id: Optional[UUID] = None

    def __init__(self, *args, execution_context: Optional["ExecutionContext"] = None, **kwargs):
        self._collect_parent_context(execution_context)
        threading.Thread.__init__(self, *args, **kwargs)

    def _collect_parent_context(self, execution_context: Optional["ExecutionContext"] = None) -> None:
        """Collect parent thread ID and trace ID from passed execution context."""
        self._parent_thread = threading.get_ident()

        # Only use explicitly passed execution context
        self._trace_id = execution_context.trace_id if execution_context else None

    def get_parent_thread(self) -> Optional[int]:
        return self._parent_thread

    def get_trace_id(self) -> Optional[UUID]:
        return self._trace_id
