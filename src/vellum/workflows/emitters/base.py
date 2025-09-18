from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.state.base import BaseState

# To protect against circular imports
if TYPE_CHECKING:
    from vellum.workflows.state.context import WorkflowContext


class BaseWorkflowEmitter(ABC):
    def __init__(self):
        self._context: Optional["WorkflowContext"] = None

    def register_context(self, context: "WorkflowContext") -> None:
        """
        Register the workflow context with this emitter.

        Args:
            context: The workflow context containing shared resources like vellum_client.
        """
        self._context = context

    @abstractmethod
    def emit_event(self, event: WorkflowEvent) -> None:
        pass

    @abstractmethod
    def snapshot_state(self, state: BaseState) -> None:
        pass

    @abstractmethod
    def join(self) -> None:
        """
        Wait for any background threads or timers used by this emitter to complete.
        This ensures all pending work is finished before the workflow terminates.
        """
        pass
