import logging
import time
from typing import Any, Dict, Optional

import httpx

from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.events.types import default_datetime_factory, default_serializer
from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.state.base import BaseState
from vellum.workflows.vellum_client import create_vellum_client

logger = logging.getLogger(__name__)


class VellumEmitter(BaseWorkflowEmitter):
    """
    Emitter that sends workflow events to Vellum's infrastructure for monitoring
    externally hosted SDK-powered workflows.

    Usage:
        class MyWorkflow(BaseWorkflow):
            emitters = [VellumEmitter]

    Configuration:
        - VELLUM_API_KEY: Environment variable for authentication
        - Or pass api_key explicitly to constructor
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: Optional[float] = 30.0,
        max_retries: int = 3,
        enabled: bool = True,
    ):
        """
        Initialize the VellumEmitter.

        Args:
            api_key: Vellum API key. If None, uses VELLUM_API_KEY environment variable.
            api_url: Custom API URL. If None, uses default Vellum environment.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts for failed requests.
            enabled: Whether emitting is enabled. Useful for development/testing.
        """
        self._enabled = enabled
        if not self._enabled:
            return

        try:
            self._client = create_vellum_client(api_key=api_key, api_url=api_url)
            self._timeout = timeout
            self._max_retries = max_retries
            self._events_endpoint = "events"  # TODO: make this configurable with the correct url
        except Exception as e:
            logger.exception(f"Failed to initialize VellumEmitter: {e}. Events will not be emitted.")
            self._enabled = False

    def emit_event(self, event: WorkflowEvent) -> None:
        """
        Emit a workflow event to Vellum's infrastructure.

        Args:
            event: The workflow event to emit.
        """
        if not self._enabled:
            return

        try:
            event_data = self._serialize_event(event)

            self._send_event(event_data)

        except Exception as e:
            logger.exception(f"Failed to emit event {event.name}: {e}")

    def snapshot_state(self, state: BaseState) -> None:
        """
        Send a state snapshot to Vellum's infrastructure.

        Args:
            state: The workflow state to snapshot.
        """
        if not self._enabled:
            return

        try:
            state_data = self._serialize_state(state)

            # Send the state snapshot as an event
            event_data = {
                "type": "workflow.state.snapshotted",
                "data": state_data,
                "timestamp": default_serializer(default_datetime_factory()),
            }

            self._send_event(event_data)

        except Exception as e:
            logger.exception(f"Failed to snapshot state: {e}")

    def _serialize_event(self, event: WorkflowEvent) -> Dict[str, Any]:
        """
        Serialize a workflow event for transmission to Vellum.

        Args:
            event: The event to serialize.

        Returns:
            Serialized event data.
        """
        # Use the same serialization approach as the rest of the system
        return {
            "type": "workflow.event",
            "data": default_serializer(event),
        }

    def _serialize_state(self, state: BaseState) -> Dict[str, Any]:
        """
        Serialize a workflow state for transmission to Vellum.

        Args:
            state: The state to serialize.

        Returns:
            Serialized state data.
        """
        return default_serializer(state)

    def _send_event(self, event_data: Dict[str, Any]) -> None:
        """
        Send event data to Vellum's events endpoint with retry logic.

        Args:
            event_data: The serialized event data to send.
        """
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                # Use the Vellum client's underlying HTTP client to make the request
                # For proper authentication headers and configuration
                base_url = self._client._client_wrapper.get_environment().default
                response = self._client._client_wrapper.httpx_client.request(
                    method="POST",
                    path=f"{base_url}/{self._events_endpoint}",  # TODO: will be replaced with the correct url
                    json=event_data,
                    headers=self._client._client_wrapper.get_headers(),
                    request_options={"timeout_in_seconds": self._timeout},
                )

                response.raise_for_status()

                if attempt > 0:
                    logger.info(f"Event sent successfully after {attempt + 1} attempts")
                return

            except httpx.HTTPStatusError as e:
                last_exception = e
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
                        logger.error(
                            f"Server error emitting event after {self._max_retries + 1} attempts: "
                            f"{e.response.status_code} {e.response.text}"
                        )
                else:
                    # Client errors (4xx) are not retriable
                    logger.error(f"Client error emitting event: {e.response.status_code} {e.response.text}")
                    raise

            except httpx.RequestError as e:
                last_exception: Optional[Exception] = e
                if attempt < self._max_retries:
                    wait_time = min(2**attempt, 60)  # Exponential backoff, max 60s
                    logger.warning(
                        f"Network error emitting event (attempt {attempt + 1}/{self._max_retries + 1}): "
                        f"{e}. Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Network error emitting event after {self._max_retries + 1} attempts: {e}")

        if last_exception:
            raise last_exception
