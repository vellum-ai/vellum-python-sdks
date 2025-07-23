"""Monitoring execution context for workflow tracing."""

from contextlib import contextmanager
from dataclasses import field
import threading
from uuid import UUID
from typing import Dict, Iterator, Optional

from vellum.client.core import UniversalBaseModel
from vellum.workflows.context import get_execution_context
from vellum.workflows.events.types import ParentContext


class MonitoringExecutionContext(UniversalBaseModel):
    """Monitoring-specific execution context that runs in parallel with ExecutionContext."""

    trace_id: UUID = field(default_factory=lambda: UUID("00000000-0000-0000-0000-000000000000"))
    parent_context: Optional[ParentContext] = None
    monitoring_enabled: bool = True


# Thread-local storage for monitoring execution context
_monitoring_execution_context: threading.local = threading.local()


class _MonitoringContextStore:
    """Thread-safe store for persisting monitoring context across execution boundaries."""

    def __init__(self):
        self._contexts: Dict[str, ParentContext] = {}
        self._thread_contexts: Dict[int, ParentContext] = {}
        self._lock = threading.Lock()
        self._current_trace_id: Optional[UUID] = None

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
            self._contexts[span_key] = parent_context

            thread_key = f"trace:{str(trace_id)}:thread:{thread_id}"
            self._contexts[thread_key] = parent_context

            # Store by trace_id for broad compatibility
            trace_key = str(trace_id)
            if trace_key != str(default_uuid):
                self._contexts[trace_key] = parent_context

            # Thread-based fallback
            self._thread_contexts[thread_id] = parent_context

    def retrieve_context(
        self, trace_id: UUID, current_parent_context: Optional[ParentContext] = None
    ) -> Optional[ParentContext]:
        """Retrieve monitoring parent context with multiple fallback strategies."""
        thread_id = threading.get_ident()
        default_uuid = UUID("00000000-0000-0000-0000-000000000000")

        with self._lock:
            # Try span_id if we have current parent context (most specific)
            if current_parent_context and hasattr(current_parent_context, "span_id"):
                span_key = f"span:{str(current_parent_context.span_id)}"
                if span_key in self._contexts:
                    return self._contexts[span_key]

            # Try trace_id + thread_id
            thread_key = f"trace:{str(trace_id)}:thread:{thread_id}"
            if thread_key in self._contexts:
                return self._contexts[thread_key]

            # Try by thread_id for current thread
            if thread_id in self._thread_contexts:
                return self._thread_contexts[thread_id]

            # Try trace_id only
            trace_key = str(trace_id)
            if trace_key != str(default_uuid) and trace_key in self._contexts:
                return self._contexts[trace_key]

            # Global current trace_id fallback for worker threads
            if trace_id == default_uuid and self._current_trace_id:
                global_trace_key = str(self._current_trace_id)
                if global_trace_key in self._contexts:
                    return self._contexts[global_trace_key]

            # Look for any recent context as last resort
            if self._thread_contexts:
                recent_thread_ids = sorted(self._thread_contexts.keys(), reverse=True)[:3]
                for recent_thread_id in recent_thread_ids:
                    if recent_thread_id in self._thread_contexts:
                        return self._thread_contexts[recent_thread_id]

            return None


# Global instance for cross-boundary context persistence
_monitoring_context_store = _MonitoringContextStore()


def get_monitoring_execution_context() -> MonitoringExecutionContext:
    """Get the current monitoring execution context."""
    try:
        context = getattr(_monitoring_execution_context, "context", None)
        if context is not None:
            return context
    except AttributeError:
        pass

    # Try to auto-create from execution context
    try:
        exec_ctx = get_execution_context()
        if exec_ctx and exec_ctx.trace_id:
            # Try to retrieve stored context first
            stored_parent = _monitoring_context_store.retrieve_context(exec_ctx.trace_id, exec_ctx.parent_context)

            if stored_parent or exec_ctx.parent_context:
                auto_context = MonitoringExecutionContext(
                    trace_id=exec_ctx.trace_id,
                    parent_context=stored_parent or exec_ctx.parent_context,
                    monitoring_enabled=True,
                )
                set_monitoring_execution_context(auto_context)
                return auto_context
    except Exception:
        pass

    # Default fallback
    default_context = MonitoringExecutionContext()
    set_monitoring_execution_context(default_context)
    return default_context


def set_monitoring_execution_context(context: MonitoringExecutionContext) -> None:
    """Set the current monitoring execution context and persist it for cross-boundary access."""
    _monitoring_execution_context.context = context

    # Store in global store for cross-boundary persistence
    if context.trace_id and context.parent_context:
        _monitoring_context_store.store_context(context.trace_id, context.parent_context)


@contextmanager
def monitoring_execution_context(
    parent_context: Optional[ParentContext] = None, trace_id: Optional[UUID] = None, monitoring_enabled: bool = True
) -> Iterator[None]:
    """Context manager for handling monitoring execution context."""
    prev_context = get_monitoring_execution_context()

    # Get current execution context to inherit trace_id if not provided
    current_exec_context = get_execution_context()
    default_uuid = UUID("00000000-0000-0000-0000-000000000000")

    # Determine trace_id to use
    if trace_id is not None:
        set_trace_id = trace_id
    elif prev_context.trace_id != default_uuid:
        set_trace_id = prev_context.trace_id
    else:
        set_trace_id = current_exec_context.trace_id or default_uuid

    # Determine parent context to use
    set_parent_context: Optional[ParentContext]
    if parent_context is not None:
        set_parent_context = parent_context
    elif prev_context.parent_context is not None:
        set_parent_context = prev_context.parent_context
    else:
        # Try to restore from global store
        if set_trace_id != default_uuid:
            stored_parent = _monitoring_context_store.retrieve_context(set_trace_id, prev_context.parent_context)
            set_parent_context = stored_parent
        else:
            set_parent_context = None

    set_context = MonitoringExecutionContext(
        parent_context=set_parent_context, trace_id=set_trace_id, monitoring_enabled=monitoring_enabled
    )

    try:
        set_monitoring_execution_context(set_context)
        yield
    finally:
        set_monitoring_execution_context(prev_context)
