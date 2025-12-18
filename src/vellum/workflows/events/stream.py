from uuid import UUID
from typing import Generator, Generic, Iterator, Optional, TypeVar

EventType = TypeVar("EventType")


class WorkflowEventGenerator(Generic[EventType]):
    """
    Generic wrapper for event streams that exposes span_id as a top-level property
    while maintaining iterator compatibility.
    """

    def __init__(
        self,
        event_generator: Generator[EventType, None, None],
        span_id: UUID,
        event_max: Optional[int] = None,
    ):
        self._event_generator = event_generator
        self._span_id = span_id
        self._event_max = event_max

    @property
    def span_id(self) -> UUID:
        """The span_id associated with this workflow stream."""
        return self._span_id

    def __iter__(self) -> Iterator[EventType]:
        """Return self to make this object iterable."""
        return self

    def __next__(self) -> EventType:
        """Get the next event from the underlying generator."""
        event = next(self._event_generator)
        if self._event_max is not None and hasattr(event, "event_max"):
            event.event_max = self._event_max
        return event
