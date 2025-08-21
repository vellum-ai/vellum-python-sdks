from abc import ABC, abstractmethod
from uuid import UUID
from typing import TYPE_CHECKING, Iterator, Optional

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.state.base import BaseState

if TYPE_CHECKING:
    from vellum.workflows.state.context import WorkflowContext


class BaseWorkflowResolver(ABC):
    def __init__(self):
        self._context: Optional["WorkflowContext"] = None

    def register_context(self, context: "WorkflowContext") -> None:
        self._context = context

    @abstractmethod
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        pass

    @abstractmethod
    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        pass

    @abstractmethod
    def load_state(self, previous_execution_id: Optional[UUID] = None) -> BaseState:
        pass
