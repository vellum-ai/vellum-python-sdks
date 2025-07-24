"""Monitoring execution context for workflow tracing."""

from contextlib import contextmanager
import threading
from uuid import UUID
from typing import Dict, Iterator, Optional

from vellum.workflows.context import ExecutionContext
from vellum.workflows.events.types import ParentContext

# Thread-local storage for monitoring execution context
_monitoring_execution_context: threading.local = threading.local()
# Thread-local storage for current span_id
_current_span_id: threading.local = threading.local()


class _MonitoringContextStore:
    """Thread-safe storage for monitoring contexts."""

    def __init__(self):
        self._lock = threading.Lock()
        self._contexts: Dict[str, ParentContext] = {}
        self._thread_contexts: Dict[int, ParentContext] = {}
        self._current_trace_id: Optional[UUID] = None
        # self._current_span_id: Optional[UUID] = None # Removed as per edit hint

    def set_current_trace_id(self, trace_id: UUID) -> None:
        """Set the current active trace_id that should be used by all threads."""
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")
        if trace_id != default_uuid:
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

    def store_context(self, trace_id: UUID, parent_context: Optional[ParentContext]) -> None:
        """Store monitoring parent context using multiple keys for reliable retrieval."""
        if parent_context is None:
            return

        thread_id = threading.get_ident()
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")

        # Update current trace_id if this is a proper trace_id
        if trace_id != default_uuid:
            self.set_current_trace_id(trace_id)

        with self._lock:
            # Store with multiple keys for better retrieval success
            span_key = f"span:{str(parent_context.span_id)}"
            trace_thread_key = f"trace:{str(trace_id)}:thread:{thread_id}"

            # Use trace:span:thread for unique context storage
            trace_span_thread_key = f"trace:{str(trace_id)}:span:{str(parent_context.span_id)}:thread:{thread_id}"

            # Store with all keys
            self._contexts[span_key] = parent_context
            self._contexts[trace_thread_key] = parent_context
            self._contexts[trace_span_thread_key] = parent_context

            # Thread-based fallback
            self._thread_contexts[thread_id] = parent_context

    def retrieve_context_by_span_id(self, span_id: UUID) -> Optional[ParentContext]:
        """Retrieve monitoring parent context directly by span_id."""
        span_key = f"span:{str(span_id)}"
        with self._lock:
            return self._contexts.get(span_key)

    def retrieve_context(
        self, trace_id: UUID, current_parent_context: Optional[ParentContext] = None
    ) -> Optional[ParentContext]:
        """Retrieve monitoring parent context with multiple fallback strategies."""
        thread_id = threading.get_ident()
        if current_parent_context:
            pass  # Removed debug output

        with self._lock:
            # Removed debug output

            # Try span_id if we have current parent context (most specific)
            if current_parent_context and hasattr(current_parent_context, "span_id"):
                span_key = f"span:{str(current_parent_context.span_id)}"
                if span_key in self._contexts:
                    result = self._contexts[span_key]
                    return result

            # Try trace_id + thread_id (most specific)
            trace_thread_key = f"trace:{str(trace_id)}:thread:{thread_id}"
            if trace_thread_key in self._contexts:
                result = self._contexts[trace_thread_key]
                return result

            # Try thread-based fallback
            if thread_id in self._thread_contexts:
                result = self._thread_contexts[thread_id]
                return result

            # Try any context with the same trace_id (for worker threads)
            trace_prefix = f"trace:{str(trace_id)}:thread:"
            for key, context in self._contexts.items():
                if key.startswith(trace_prefix):
                    return context

        return None


# Global instance for cross-boundary context persistence
_monitoring_context_store = _MonitoringContextStore()


def get_monitoring_execution_context() -> ExecutionContext:
    """Get the current monitoring execution context, with intelligent fallback."""
    # First, try thread-local storage
    if hasattr(_monitoring_execution_context, "context"):
        context = _monitoring_execution_context.context
        return context

    # If no thread-local context, try to restore from global store using current trace_id
    trace_id = _monitoring_context_store.get_current_trace_id()
    if trace_id:
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")
        if trace_id != default_uuid:
            parent_context = _monitoring_context_store.retrieve_context(trace_id, None)
            if parent_context:
                return ExecutionContext(
                    trace_id=trace_id,
                    parent_context=parent_context,
                    monitoring_enabled=True,
                )

    # Default fallback
    return ExecutionContext()


def set_monitoring_execution_context(context: ExecutionContext) -> None:
    """Set the current monitoring execution context and persist it for cross-boundary access."""
    _monitoring_execution_context.context = context

    # Only store in global store if this context has a parent_context (i.e., it's not a default/restored context)
    # This prevents overwriting deeper contexts when restoring shallower ones
    if context.trace_id and context.parent_context:
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")
        if context.trace_id != default_uuid:
            _monitoring_context_store.store_context(context.trace_id, context.parent_context)


@contextmanager
def monitoring_execution_context(
    parent_context: Optional[ParentContext] = None, trace_id: Optional[UUID] = None, monitoring_enabled: bool = True
) -> Iterator[None]:
    """Context manager for handling monitoring execution context - self-contained monitoring system."""
    prev_context = get_monitoring_execution_context()
    default_uuid = UUID("00000000-0000-0000-0000-000000000000")

    # Determine trace_id to use
    if trace_id is not None:
        set_trace_id = trace_id
    elif prev_context.trace_id != default_uuid:
        set_trace_id = prev_context.trace_id
    else:
        # Try to get from monitoring context store
        current_trace_id = _monitoring_context_store.get_current_trace_id()
        set_trace_id = current_trace_id if current_trace_id else default_uuid

    # Determine parent context to use
    set_parent_context: Optional[ParentContext]
    if parent_context is not None:
        set_parent_context = parent_context
    elif prev_context.parent_context is not None:
        set_parent_context = prev_context.parent_context
    else:
        # Try to restore from monitoring store
        if set_trace_id != default_uuid:
            stored_parent = _monitoring_context_store.retrieve_context(set_trace_id)
            set_parent_context = stored_parent
        else:
            set_parent_context = None

    set_context = ExecutionContext(
        parent_context=set_parent_context, trace_id=set_trace_id, monitoring_enabled=monitoring_enabled
    )

    try:
        set_monitoring_execution_context(set_context)
        yield
    finally:
        set_monitoring_execution_context(prev_context)
