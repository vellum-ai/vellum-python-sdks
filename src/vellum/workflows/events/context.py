"""Monitoring execution context for workflow tracing."""

import threading
from uuid import UUID
from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:
    from vellum.workflows.context import ExecutionContext

DEFAULT_TRACE_ID = UUID("00000000-0000-0000-0000-000000000000")


class MonitoringContextStore:
    """
    thread-safe storage for monitoring contexts.
    handles context persistence and retrieval across threads.
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
        """Store monitoring parent context using thread_id:trace_id keys."""
        thread_id = threading.get_ident()
        trace_id = context.trace_id

        with self._lock:
            # Always use thread_id:trace_id format
            context_key = f"thread:{thread_id}:trace:{trace_id}"
            self._contexts[context_key] = context

    def retrieve_context(self) -> Optional["ExecutionContext"]:
        """Retrieve monitoring parent context using trace_id from thread."""
        current_thread_id = threading.get_ident()
        current_thread = threading.current_thread()

        # Get trace_id directly from the thread if it's a RelationalThread
        trace_id = None
        if hasattr(current_thread, "get_trace_id"):
            trace_id = current_thread.get_trace_id()

        # If no trace_id on current thread, try to get it from parent thread
        if not trace_id and hasattr(current_thread, "get_parent_thread"):
            parent_thread_id = current_thread.get_parent_thread()
            if parent_thread_id:
                # Find parent thread and get its trace_id
                for t in threading.enumerate():
                    if t.ident == parent_thread_id and hasattr(t, "get_trace_id"):
                        trace_id = t.get_trace_id()
                        if trace_id:
                            break

        if not trace_id:
            return None

        with self._lock:
            # Try current thread with trace_id
            current_key = f"thread:{current_thread_id}:trace:{trace_id}"
            if current_key in self._contexts:
                return self._contexts[current_key]

            # Try parent thread with same trace_id (child inherits parent's trace)
            if hasattr(current_thread, "get_parent_thread"):
                parent_thread_id = current_thread.get_parent_thread()
                if parent_thread_id:
                    parent_key = f"thread:{parent_thread_id}:trace:{trace_id}"
                    if parent_key in self._contexts:
                        return self._contexts[parent_key]

        return None

    def clear_context(self):
        """Clear all stored contexts."""
        with self._lock:
            self._contexts.clear()
