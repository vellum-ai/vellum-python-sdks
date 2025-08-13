import logging
from typing import Optional

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

    def emit_event(self, event: SDKWorkflowEvent) -> None:
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
            self._send_event(event)

        except Exception as e:
            logger.exception(f"Failed to emit event {event.name}: {e}")

    def snapshot_state(self, state: BaseState) -> None:
        """
        Send a state snapshot to Vellum's infrastructure.

        Args:
            state: The workflow state to snapshot.
        """
        pass

    def _send_event(self, event: SDKWorkflowEvent) -> None:
        """
        Send event to Vellum's events endpoint using client.events.create.

        Args:
            event: The WorkflowEvent object to send.
        """
        if not self._context:
            logger.warning("Cannot send event: No workflow context registered")
            return

        client = self._context.vellum_client
        request_options = RequestOptions(timeout_in_seconds=self._timeout, max_retries=self._max_retries)
        client.events.create(
            # The API accepts a ClientWorkflowEvent but our SDK emits an SDKWorkflowEvent. These shapes are
            # meant to be identical, just with different helper methods. We may consolidate the two in the future.
            # But for now, the type ignore allows us to avoid an additional Model -> json -> Model conversion.
            request=event,  # type: ignore[arg-type]
            request_options=request_options,
        )
