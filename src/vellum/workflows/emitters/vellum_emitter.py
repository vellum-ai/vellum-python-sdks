import logging
import time
from typing import Any, Dict, Optional

import httpx

from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.events.types import default_serializer
from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.state.base import BaseState

logger = logging.getLogger(__name__)


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
        self._events_endpoint = "v1/events"  # TODO: make this configurable with the correct url

    def emit_event(self, event: WorkflowEvent) -> None:
        """
        Emit a workflow event to Vellum's infrastructure.

        Args:
            event: The workflow event to emit.
        """
        if not self._context:
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
        Send event data to Vellum's events endpoint with retry logic.

        Args:
            event_data: The serialized event data to send.
        """
        if not self._context:
            logger.warning("Cannot send event: No workflow context registered")
            return

        client = self._context.vellum_client

        for attempt in range(self._max_retries + 1):
            try:
                # Use the Vellum client's underlying HTTP client to make the request
                # For proper authentication headers and configuration
                base_url = client._client_wrapper.get_environment().default
                response = client._client_wrapper.httpx_client.request(
                    method="POST",
                    base_url=base_url,
                    path=self._events_endpoint,  # TODO: will be replaced with the correct url
                    json=event_data,
                    headers=client._client_wrapper.get_headers(),
                    request_options={"timeout_in_seconds": self._timeout},
                )

                response.raise_for_status()

                if attempt > 0:
                    logger.info(f"Event sent successfully after {attempt + 1} attempts")
                return

            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    # Server errors might be transient, retry
                    if attempt < self._max_retries:
                        wait_time = min(2**attempt, 60)  # Exponential backoff, max 60s
                        logger.warning(
                            f"Server error emitting event (attempt {attempt + 1}/{self._max_retries + 1}): "
                            f"{e.response.status_code}. Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.exception(
                            f"Server error emitting event after {self._max_retries + 1} attempts: "
                            f"{e.response.status_code} {e.response.text}"
                        )
                        return
                else:
                    # Client errors (4xx) are not retriable
                    logger.exception(f"Client error emitting event: {e.response.status_code} {e.response.text}")
                    return

            except httpx.RequestError as e:
                if attempt < self._max_retries:
                    wait_time = min(2**attempt, 60)  # Exponential backoff, max 60s
                    logger.warning(
                        f"Network error emitting event (attempt {attempt + 1}/{self._max_retries + 1}): "
                        f"{e}. Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.exception(f"Network error emitting event after {self._max_retries + 1} attempts: {e}")
                    return
