import logging
import threading
from typing import List, Optional

from vellum.core.request_options import RequestOptions
from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.events.workflow import WorkflowEvent as SDKWorkflowEvent
from vellum.workflows.state.base import BaseState

logger = logging.getLogger(__name__)

DISALLOWED_EVENTS = {"workflow.execution.streaming", "node.execution.streaming"}


class VellumEmitter(BaseWorkflowEmitter):
    """
    Emitter that sends workflow events to Vellum's infrastructure for monitoring
    externally hosted SDK-powered workflows.

    Usage:
        class MyWorkflow(BaseWorkflow):
            emitters = [VellumEmitter]

    The emitter will automatically use the same Vellum client configuration
    as the workflow it's attached to.
    """

    def __init__(
        self,
        *,
        timeout: Optional[float] = 30.0,
        max_retries: int = 3,
        debounce_timeout: float = 0.1,
    ):
        """
        Initialize the VellumEmitter.

        Args:
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            debounce_timeout: Time in seconds to wait before sending batched events.
        """
        super().__init__()
        self._timeout = timeout
        self._max_retries = max_retries
        self._debounce_timeout = debounce_timeout
        self._event_queue: List[SDKWorkflowEvent] = []
        self._queue_lock = threading.Lock()
        self._debounce_timer: Optional[threading.Timer] = None

    def emit_event(self, event: SDKWorkflowEvent) -> None:
        """
        Queue a workflow event for batched emission to Vellum's infrastructure.

        Args:
            event: The workflow event to emit.
        """
        if not self._context:
            return

        if event.name in DISALLOWED_EVENTS:
            return

        try:
            with self._queue_lock:
                self._event_queue.append(event)

                if self._debounce_timer:
                    self._debounce_timer.cancel()

                self._debounce_timer = threading.Timer(self._debounce_timeout, self._flush_events)
                self._debounce_timer.start()

        except Exception as e:
            logger.exception(f"Failed to queue event {event.name}: {e}")

    def _flush_events(self) -> None:
        """
        Send all queued events as a batch to Vellum's infrastructure.
        """
        with self._queue_lock:
            if not self._event_queue:
                return

            events_to_send = self._event_queue.copy()
            self._event_queue.clear()
            self._debounce_timer = None

        try:
            self._send_events(events_to_send)
        except Exception as e:
            logger.exception(f"Failed to send batched events: {e}")

    def __del__(self) -> None:
        """
        Cleanup: flush any pending events and cancel timer.
        """
        try:
            if self._debounce_timer:
                self._debounce_timer.cancel()
            self._flush_events()
        except Exception:
            pass

    def snapshot_state(self, state: BaseState) -> None:
        """
        Send a state snapshot to Vellum's infrastructure.

        Args:
            state: The workflow state to snapshot.
        """
        pass

    def _send_events(self, events: List[SDKWorkflowEvent]) -> None:
        """
        Send events to Vellum's events endpoint using client.events.create.

        Args:
            events: List of WorkflowEvent objects to send.
        """
        if not self._context:
            logger.warning("Cannot send events: No workflow context registered")
            return

        if not events:
            return

        client = self._context.vellum_client
        request_options = RequestOptions(timeout_in_seconds=self._timeout, max_retries=self._max_retries)

        client.events.create(
            # The API accepts a ClientWorkflowEvent but our SDK emits an SDKWorkflowEvent. These shapes are
            # meant to be identical, just with different helper methods. We may consolidate the two in the future.
            # But for now, the type ignore allows us to avoid an additional Model -> json -> Model conversion.
            request=events,  # type: ignore[arg-type]
            request_options=request_options,
        )
