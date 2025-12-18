from uuid import UUID
from typing import Generator, Generic, Iterator, TypeVar

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
