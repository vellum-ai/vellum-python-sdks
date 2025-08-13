import logging
from typing import Any, Optional

from vellum.client.types import (
    VellumCodeResourceDefinition as SDKVellumCodeResourceDefinition,
    WorkflowExecutionFulfilledBody as SDKWorkflowExecutionFulfilledBody,
    WorkflowExecutionFulfilledEvent as SDKWorkflowExecutionFulfilledEvent,
    WorkflowExecutionInitiatedBody as SDKWorkflowExecutionInitiatedBody,
    WorkflowExecutionInitiatedEvent as SDKWorkflowExecutionInitiatedEvent,
    WorkflowExecutionPausedBody as SDKWorkflowExecutionPausedBody,
    WorkflowExecutionPausedEvent as SDKWorkflowExecutionPausedEvent,
    WorkflowExecutionRejectedBody as SDKWorkflowExecutionRejectedBody,
    WorkflowExecutionRejectedEvent as SDKWorkflowExecutionRejectedEvent,
    WorkflowExecutionResumedBody as SDKWorkflowExecutionResumedBody,
    WorkflowExecutionResumedEvent as SDKWorkflowExecutionResumedEvent,
    WorkflowExecutionSnapshottedBody as SDKWorkflowExecutionSnapshottedBody,
    WorkflowExecutionSnapshottedEvent as SDKWorkflowExecutionSnapshottedEvent,
    WorkflowExecutionStreamingBody as SDKWorkflowExecutionStreamingBody,
    WorkflowExecutionStreamingEvent as SDKWorkflowExecutionStreamingEvent,
)
from vellum.core.request_options import RequestOptions
from vellum.workflows.emitters.base import BaseWorkflowEmitter
from vellum.workflows.events.types import default_serializer
from vellum.workflows.events.workflow import WorkflowEvent, is_workflow_event
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

    def _convert_workflow_event_to_sdk_event(self, event: WorkflowEvent) -> Any:
        """
        Convert a workflow event to SDK client event format.

        Args:
            event: The WorkflowEvent to convert

        Returns:
            SDK client event compatible with client.events.create
        """
        if not is_workflow_event(event):
            raise ValueError(f"Event {event.name} is not a workflow execution event")

        workflow_def_data = default_serializer(event.body.workflow_definition)
        sdk_workflow_definition = SDKVellumCodeResourceDefinition(
            name=workflow_def_data["name"], module=workflow_def_data["module"], id=workflow_def_data["id"]
        )

        if event.name == "workflow.execution.initiated":
            inputs_data = default_serializer(event.body.inputs)
            sdk_body = SDKWorkflowExecutionInitiatedBody(
                workflow_definition=sdk_workflow_definition, inputs=inputs_data
            )
            return SDKWorkflowExecutionInitiatedEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=sdk_body,
            )
        elif event.name == "workflow.execution.streaming":
            output_data = default_serializer(event.body.output)
            return SDKWorkflowExecutionStreamingEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=SDKWorkflowExecutionStreamingBody(workflow_definition=sdk_workflow_definition, output=output_data),
            )
        elif event.name == "workflow.execution.fulfilled":
            outputs_data = default_serializer(event.body.outputs)
            return SDKWorkflowExecutionFulfilledEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=SDKWorkflowExecutionFulfilledBody(
                    workflow_definition=sdk_workflow_definition, outputs=outputs_data
                ),
            )
        elif event.name == "workflow.execution.rejected":
            error_data = default_serializer(event.body.error)
            return SDKWorkflowExecutionRejectedEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=SDKWorkflowExecutionRejectedBody(workflow_definition=sdk_workflow_definition, error=error_data),
            )
        elif event.name == "workflow.execution.paused":
            external_inputs_data = default_serializer(event.body.external_inputs)
            return SDKWorkflowExecutionPausedEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=SDKWorkflowExecutionPausedBody(
                    workflow_definition=sdk_workflow_definition, external_inputs=external_inputs_data
                ),
            )
        elif event.name == "workflow.execution.resumed":
            return SDKWorkflowExecutionResumedEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=SDKWorkflowExecutionResumedBody(workflow_definition=sdk_workflow_definition),
            )
        elif event.name == "workflow.execution.snapshotted":
            state_data = default_serializer(event.body.state)
            return SDKWorkflowExecutionSnapshottedEvent(
                id=str(event.id),
                timestamp=event.timestamp,
                trace_id=str(event.trace_id),
                span_id=str(event.span_id),
                parent=event.parent,
                body=SDKWorkflowExecutionSnapshottedBody(workflow_definition=sdk_workflow_definition, state=state_data),
            )
        else:
            raise ValueError(f"Unsupported event type: {event.name}")

    def _send_event(self, event: WorkflowEvent) -> None:
        """
        Send event to Vellum's events endpoint using client.events.create.

        Args:
            event: The WorkflowEvent object to send.
        """
        if not self._context:
            logger.warning("Cannot send event: No workflow context registered")
            return

        client = self._context.vellum_client

        try:
            sdk_event = self._convert_workflow_event_to_sdk_event(event)

            request_options = RequestOptions(timeout_in_seconds=self._timeout, max_retries=self._max_retries)

            client.events.create(request=sdk_event, request_options=request_options)

            logger.debug("Event sent successfully via client.events.create")
            return

        except Exception as e:
            logger.exception(f"Failed to send event via client.events.create: {e}")
            return
