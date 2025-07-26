"""Monitoring execution context for workflow tracing."""

import threading
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional, Type

DEFAULT_TRACE_ID = UUID("00000000-0000-0000-0000-000000000000")

# Thread-local storage for monitoring execution context
_monitoring_execution_context: threading.local = threading.local()
# Thread-local storage for current span_id
_current_span_id: threading.local = threading.local()

if TYPE_CHECKING:
    from vellum.workflows.context import ExecutionContext


class MonitoringContextStore:
    """
    thread-safe storage for monitoring contexts.
    handles context persistence and retrieval across threads.
    relies on the execution context manager for manual retrieval
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._contexts: Dict[str, Type["ExecutionContext"]] = {}

    def get_current_trace_id(self) -> Optional[UUID]:
        """Get the current active trace_id that should be used by all threads."""
        with self._lock:
            return self.retrieve_context().trace_id

    def store_context(self, context: Optional["ExecutionContext"]) -> None:
        """Store monitoring parent context using multiple keys for reliable retrieval."""
        # Use the context's trace_id if available, otherwise use the current trace_id
        thread_id = threading.get_ident()

        with self._lock:
            # Use trace:span:thread for unique context storage
            thread_key = f"thread:{str(thread_id)}"
            self._contexts[thread_key] = context

    def retrieve_context(self) -> Optional[Type["ExecutionContext"]]:
        """Retrieve monitoring parent context with multiple fallback strategies."""
        with self._lock:
            # Try exact match first
            thread = threading.current_thread()
            parent_thread = thread.get_parent_thread() if hasattr(thread, "get_parent_thread") else thread.ident
            span_key = f"thread:{parent_thread}"
            backup_key = f"thread:{str(thread.ident)}"
            if backup_key in self._contexts:
                result = self._contexts[backup_key]
                return result
            if span_key in self._contexts:
                result = self._contexts[span_key]
                return result

        return None

    def clear_context(self):
        self._contexts = {}
        self._current_trace_id = None
