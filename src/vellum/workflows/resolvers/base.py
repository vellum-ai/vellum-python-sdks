from abc import ABC, abstractmethod
from uuid import UUID
from typing import TYPE_CHECKING, Iterator, Optional, Type, Union

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.resolvers.types import LoadStateResult
from vellum.workflows.state.base import BaseState

if TYPE_CHECKING:
    from vellum.workflows.state.context import WorkflowContext
    from vellum.workflows.workflows.base import BaseWorkflow


class BaseWorkflowResolver(ABC):
    def __init__(self):
        self._context: Optional["WorkflowContext"] = None
        self._workflow_class: Optional[Type["BaseWorkflow"]] = None

    def register_workflow_instance(self, workflow_instance: "BaseWorkflow") -> None:
        self._workflow_class = type(workflow_instance)
        self._context = workflow_instance.context

    @abstractmethod
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        pass

    @abstractmethod
    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        pass

    @abstractmethod
    def load_state(self, previous_execution_id: Optional[Union[UUID, str]] = None) -> Optional[LoadStateResult]:
        pass
