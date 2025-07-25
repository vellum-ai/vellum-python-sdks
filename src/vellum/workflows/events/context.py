"""Monitoring execution context for workflow tracing."""

import threading
from uuid import UUID
from typing import Dict, Optional

from vellum.workflows.context import ExecutionContext

DEFAULT_TRACE_ID = UUID("00000000-0000-0000-0000-000000000000")

# Thread-local storage for monitoring execution context
_monitoring_execution_context: threading.local = threading.local()
# Thread-local storage for current span_id
_current_span_id: threading.local = threading.local()


class _MonitoringContextStore:
    """
    thread-safe storage for monitoring contexts.
    handles context persistence and retrieval across threads.
    relies on the execution context manager for manual retrieval
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._contexts: Dict[str, ExecutionContext] = {}
        self._thread_contexts: Dict[int, ExecutionContext] = {}
        self._current_trace_id: Optional[UUID] = None

    def set_current_trace_id(self, trace_id: UUID) -> None:
        """Set the current active trace_id that should be used by all threads."""
        if trace_id != DEFAULT_TRACE_ID:
            with self._lock:
                self._current_trace_id = trace_id

    def get_current_trace_id(self) -> Optional[UUID]:
        """Get the current active trace_id that should be used by all threads."""
        with self._lock:
            return self._current_trace_id

    def set_current_span_id(self, span_id: UUID) -> None:
        """Set the current active span_id for this thread."""
        _current_span_id.span_id = span_id

    def get_current_span_id(self) -> Optional[UUID]:
        """Get the current active span_id for this thread."""
        return getattr(_current_span_id, "span_id", None)

    def store_context(self, context: Optional[ExecutionContext]) -> None:
        """Store monitoring parent context using multiple keys for reliable retrieval."""
        if not context or context.parent_context is None:
            return

        thread_id = threading.get_ident()
        trace_id = self.get_current_trace_id()
        if context.trace_id != DEFAULT_TRACE_ID and trace_id is None:
            self.set_current_trace_id(context.trace_id)

        with self._lock:
            # Use trace:span:thread for unique context storage
            trace_span_thread_key = (
                f"trace:{str(trace_id)}:span:{str(context.parent_context.span_id)}:thread:{thread_id}"
            )
            self._contexts[trace_span_thread_key] = context

    def retrieve_context(self, trace_id: UUID, span_id: Optional[UUID] = None) -> Optional[ExecutionContext]:
        """Retrieve monitoring parent context with multiple fallback strategies."""
        thread_id = threading.get_ident()
        with self._lock:
            if not span_id:
                span_id = getattr(_current_span_id, "span_id", None)
                if not span_id:
                    return None

            span_key = f"trace:{str(trace_id)}:span:{str(span_id)}:thread:{thread_id}"
            if span_key in self._contexts:
                result = self._contexts[span_key]
                return result

        return None


# Global instance for cross-boundary context persistence
_monitoring_context_store = _MonitoringContextStore()


def get_monitoring_execution_context() -> ExecutionContext:
    """Get the current monitoring execution context, with intelligent fallback."""
    if hasattr(_monitoring_execution_context, "context"):
        context = _monitoring_execution_context.context
        if context.trace_id != DEFAULT_TRACE_ID and context.parent_context:
            return context

    # If no thread-local context, try to restore from global store using current trace_id
    trace_id = _monitoring_context_store.get_current_trace_id()
    span_id = _current_span_id.span_id if hasattr(_current_span_id, "span_id") else None
    if trace_id:
        if trace_id != DEFAULT_TRACE_ID:
            context = _monitoring_context_store.retrieve_context(trace_id, span_id)
            if context:
                _monitoring_execution_context.context = context
                return context
    return ExecutionContext()


def set_monitoring_execution_context(context: ExecutionContext) -> None:
    """Set the current monitoring execution context and persist it for cross-boundary access."""
    _monitoring_execution_context.context = context

    if context.trace_id and context.parent_context:
        _monitoring_context_store.store_context(context)
