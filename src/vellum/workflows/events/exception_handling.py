from uuid import uuid4
from typing import Generator

from vellum.workflows.context import get_execution_context
from vellum.workflows.events.stream import WorkflowEventGenerator
from vellum.workflows.events.workflow import (
    WorkflowEvent,
    WorkflowEventStream,
    WorkflowExecutionInitiatedBody,
    WorkflowExecutionInitiatedEvent,
    WorkflowExecutionRejectedBody,
    WorkflowExecutionRejectedEvent,
)
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs import BaseInputs


def stream_initialization_exception(
    exception: WorkflowInitializationException,
) -> WorkflowEventStream:
    """
    Stream a workflow initiated event followed by a workflow rejected event for an initialization exception.

    Args:
        exception: The WorkflowInitializationException to stream events for

    Returns:
        WorkflowEventGenerator yielding initiated and rejected events
    """

    execution_context = get_execution_context()
    span_id = uuid4()

    def _generate_events() -> Generator[WorkflowEvent, None, None]:
        initiated_event: WorkflowEvent = WorkflowExecutionInitiatedEvent(
            trace_id=execution_context.trace_id,
            span_id=span_id,
            body=WorkflowExecutionInitiatedBody(
                workflow_definition=exception.definition,
                inputs=BaseInputs(),
                initial_state=None,
            ),
            parent=execution_context.parent_context,
        )
        yield initiated_event

        rejected_event = WorkflowExecutionRejectedEvent(
            trace_id=execution_context.trace_id,
            span_id=span_id,
            body=WorkflowExecutionRejectedBody(
                workflow_definition=exception.definition,
                error=exception.error,
            ),
            parent=execution_context.parent_context,
        )
        yield rejected_event

    return WorkflowEventGenerator(_generate_events(), span_id)
