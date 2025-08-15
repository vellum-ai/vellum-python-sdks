import threading
from uuid import UUID
from typing import Optional


class RelationalThread(threading.Thread):
    _parent_thread: Optional[int] = None
    _trace_id: Optional[UUID] = None

    def __init__(self, *args, **kwargs):
        self._collect_parent_context()
        threading.Thread.__init__(self, *args, **kwargs)

    def _collect_parent_context(self) -> None:
        """Collect parent thread ID and trace ID from current execution context."""
        self._parent_thread = threading.get_ident()

        # Import here to avoid circular imports
        from vellum.workflows.context import get_execution_context

        try:
            current_context = get_execution_context()
            self._trace_id = current_context.trace_id if current_context else None
        except Exception:
            # If we can't get the execution context, that's okay - we'll fall back to None
            self._trace_id = None

    def get_parent_thread(self) -> Optional[int]:
        return self._parent_thread

    def get_trace_id(self) -> Optional[UUID]:
        return self._trace_id
