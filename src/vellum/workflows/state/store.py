from typing import Iterator, List

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.state.base import BaseState


class Store:
    def __init__(self) -> None:
        self._events: List[WorkflowEvent] = []
        self._state_snapshots: List[BaseState] = []

    def append_event(self, event: WorkflowEvent) -> None:
        self._events.append(event)

    def append_state_snapshot(self, state: BaseState) -> None:
        self._state_snapshots.append(state)

    def clear(self) -> None:
        self._events = []
        self._state_snapshots = []

    @property
    def events(self) -> Iterator[WorkflowEvent]:
        return iter(self._events)

    @property
    def state_snapshots(self) -> Iterator[BaseState]:
        return iter(self._state_snapshots)


class EmptyStore(Store):
    """
    A store that does not record any events or state snapshots, for workflows
    that want to opt out of the memory footprint of the traditional store entirely.
    """

    def append_event(self, event: WorkflowEvent) -> None:
        pass

    def append_state_snapshot(self, state: BaseState) -> None:
        pass
