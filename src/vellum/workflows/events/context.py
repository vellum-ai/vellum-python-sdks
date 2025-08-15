"""Monitoring execution context for workflow tracing."""

import threading
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional

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
    leverages RelationalThread's parent-child relationships and trace tracking
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._contexts: Dict[str, "ExecutionContext"] = {}

    def get_current_trace_id(self) -> Optional[UUID]:
        """Get the current active trace_id that should be used by all threads."""
        with self._lock:
            current_context = self.retrieve_context()
            return current_context.trace_id if current_context else None

    def store_context(self, context: "ExecutionContext") -> None:
        """Store monitoring parent context using simple thread-based keys."""
        thread_id = threading.get_ident()

        with self._lock:
            # Simple thread-based storage - RelationalThread handles the relationships
            context_key = f"thread:{thread_id}"
            self._contexts[context_key] = context

    def retrieve_context(self) -> Optional["ExecutionContext"]:
        """Retrieve monitoring parent context using RelationalThread relationships."""
        current_thread_id = threading.get_ident()
        current_thread = threading.current_thread()

        with self._lock:
            # Strategy 1: Try current thread
            thread_key = f"thread:{current_thread_id}"
            if thread_key in self._contexts:
                return self._contexts[thread_key]

            # Strategy 2: If this is a RelationalThread, try parent thread
            if hasattr(current_thread, "get_parent_thread"):
                parent_thread_id = current_thread.get_parent_thread()
                if parent_thread_id:
                    parent_key = f"thread:{parent_thread_id}"
                    if parent_key in self._contexts:
                        return self._contexts[parent_key]

            # Strategy 3: If RelationalThread has trace_id, find matching context
            if hasattr(current_thread, "get_trace_id"):
                thread_trace_id = current_thread.get_trace_id()
                if thread_trace_id:
                    # Find any context with matching trace_id
                    for context in self._contexts.values():
                        if context.trace_id == thread_trace_id:
                            return context

        return None

    def clear_context(self):
        """Clear all stored contexts."""
        with self._lock:
            self._contexts.clear()
