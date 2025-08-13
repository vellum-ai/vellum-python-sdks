import logging
from typing import Any, Dict, Optional

from vellum.core.request_options import RequestOptions
from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.events.types import default_serializer
from vellum.workflows.events.workflow import WorkflowEvent
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
    ):
        """
        Initialize the VellumEmitter.

        Args:
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
        """
        super().__init__()
        self._timeout = timeout
        self._max_retries = max_retries

    def emit_event(self, event: WorkflowEvent) -> None:
        """
        Emit a workflow event to Vellum's infrastructure.

        Args:
            event: The workflow event to emit.
        """
        if not self._context:
            return

        if event.name in DISALLOWED_EVENTS:
            return

        try:
            event_data = default_serializer(event)
            self._send_event(event_data)

        except Exception as e:
            logger.exception(f"Failed to emit event {event.name}: {e}")

    def snapshot_state(self, state: BaseState) -> None:
        """
        Send a state snapshot to Vellum's infrastructure.

        Args:
            state: The workflow state to snapshot.
        """
        pass

    def _send_event(self, event_data: Dict[str, Any]) -> None:
        """
        Send event data to Vellum's events endpoint using the SDK client.

        Args:
            event_data: The serialized event data to send.
        """
        if not self._context:
            logger.warning("Cannot send event: No workflow context registered")
            return

        client = self._context.vellum_client

        try:
            # Use the SDK's built-in retry mechanism via RequestOptions
            request_options = RequestOptions(timeout_in_seconds=self._timeout, max_retries=self._max_retries)

            # Use the SDK's underlying HTTP client with proper retry handling
            client._client_wrapper.httpx_client.request(
                "monitoring/v1/events",
                base_url=client._client_wrapper.get_environment().default,
                method="POST",
                json=event_data,
                headers={
                    "content-type": "application/json",
                    **client._client_wrapper.get_headers(),
                },
                request_options=request_options,
            )

            logger.debug("Event sent successfully via SDK client")
            return

        except Exception as e:
            logger.exception(f"Failed to send event via SDK client: {e}")
            return
