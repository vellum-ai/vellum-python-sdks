from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Generator, Generic, Iterator, TypeVar

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent
    from vellum.workflows.exceptions import WorkflowInitializationException

EventType = TypeVar("EventType")


class WorkflowEventGenerator(Generic[EventType]):
    """
    Generic wrapper for event streams that exposes span_id as a top-level property
    while maintaining iterator compatibility.
    """

    def __init__(self, event_generator: Generator[EventType, None, None], span_id: UUID):
        self._event_generator = event_generator
        self._span_id = span_id

    @property
    def span_id(self) -> UUID:
        """The span_id associated with this workflow stream."""
        return self._span_id

    def __iter__(self) -> Iterator[EventType]:
        """Return self to make this object iterable."""
        return self

    def __next__(self) -> EventType:
        """Get the next event from the underlying generator."""
        return next(self._event_generator)

    @staticmethod
    def stream_initialization_exception(
        exception: "WorkflowInitializationException",
    ) -> "WorkflowEventGenerator[WorkflowEvent]":
        """
        Stream a workflow initiated event followed by a workflow rejected event for an initialization exception.

        Args:
            exception: The WorkflowInitializationException to stream events for

        Returns:
            WorkflowEventGenerator yielding initiated and rejected events
        """
        from vellum.workflows.context import get_execution_context
        from vellum.workflows.events.workflow import (
            WorkflowEvent,
            WorkflowExecutionInitiatedBody,
            WorkflowExecutionInitiatedEvent,
            WorkflowExecutionRejectedBody,
            WorkflowExecutionRejectedEvent,
        )
        from vellum.workflows.inputs import BaseInputs

        execution_context = get_execution_context()
        span_id = uuid4()

        def _generate_events() -> Generator["WorkflowEvent", None, None]:
            initiated_event: "WorkflowEvent" = WorkflowExecutionInitiatedEvent(
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
