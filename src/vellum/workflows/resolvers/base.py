from abc import ABC, abstractmethod
from uuid import UUID
from typing import TYPE_CHECKING, Iterator, Optional, Type

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.state.base import BaseState

if TYPE_CHECKING:
    from vellum.workflows.state.context import WorkflowContext
    from vellum.workflows.workflows.base import BaseWorkflow


class BaseWorkflowResolver(ABC):
    def __init__(self):
        self._context: Optional["WorkflowContext"] = None
        self._workflow_class: Optional[Type["BaseWorkflow"]] = None

    def register_context(self, context: "WorkflowContext") -> None:
        self._context = context

    def register_workflow(self, workflow_class: Type["BaseWorkflow"]) -> None:
        self._workflow_class = workflow_class

    @abstractmethod
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        pass

    @abstractmethod
    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        pass

    @abstractmethod
    def load_state(self, previous_execution_id: Optional[UUID] = None) -> Optional[BaseState]:
        pass
