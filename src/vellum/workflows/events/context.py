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
        """Store monitoring parent context using trace:span:thread keys."""
        thread_id = threading.get_ident()
        current_thread = threading.current_thread()
        trace_id = context.trace_id

        with self._lock:
            # Get span_id from RelationalThread first
            span_id = None

            if context.parent_context and hasattr(context.parent_context, "span_id"):
                span_id = context.parent_context.span_id

            if not span_id and hasattr(current_thread, "get_parent_span_id"):
                span_id = current_thread.get_parent_span_id()

            # Always use trace:span:thread format - require span_id
            if span_id:
                context_key = f"trace:{str(trace_id)}:span:{str(span_id)}:thread:{thread_id}"
                self._contexts[context_key] = context

    def retrieve_context(self) -> Optional["ExecutionContext"]:
        """Retrieve monitoring parent context using trace:span:thread keys."""
        current_thread = threading.current_thread()
        current_thread_id = current_thread.ident

        # Get trace_id and span_id directly from the thread if it's a RelationalThread
        trace_id = None
        span_id = None
        if hasattr(current_thread, "get_trace_id"):
            trace_id = current_thread.get_trace_id()
        if hasattr(current_thread, "get_parent_span_id"):
            span_id = current_thread.get_parent_span_id()

        # Require both trace_id and span_id - no fallback searching
        if not trace_id or not span_id:
            return None

        with self._lock:
            # Try current thread
            current_key = f"trace:{str(trace_id)}:span:{str(span_id)}:thread:{current_thread_id}"
            if current_key in self._contexts:
                return self._contexts[current_key]

            # Try parent thread with same trace and span
            if hasattr(current_thread, "get_parent_thread"):
                parent_thread_id = current_thread.get_parent_thread()
                if parent_thread_id:
                    parent_key = f"trace:{str(trace_id)}:span:{str(span_id)}:thread:{parent_thread_id}"
                    if parent_key in self._contexts:
                        return self._contexts[parent_key]

        return None

    def clear_context(self):
        """Clear all stored contexts."""
        with self._lock:
            self._contexts.clear()
