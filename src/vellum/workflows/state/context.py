from functools import cached_property
from queue import Queue
from typing import TYPE_CHECKING, List, Optional

from vellum import Vellum
from vellum.workflows.events.types import ParentContext
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.types.cycle_map import CycleMap
from vellum.workflows.vellum_client import create_vellum_client

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent


class WorkflowContext:
    def __init__(
        self,
        *,
        vellum_client: Optional[Vellum] = None,
        parent_context: Optional[ParentContext] = None,
        node_output_mocks: Optional[List[BaseOutputs]] = None,
    ):
        self._vellum_client = vellum_client
        self._parent_context = parent_context
        self._event_queue: Optional[Queue["WorkflowEvent"]] = None
        self._node_output_mocks_map = CycleMap(items=node_output_mocks or [], key_by=lambda mock: mock.__class__)

    @cached_property
    def vellum_client(self) -> Vellum:
        if self._vellum_client:
            return self._vellum_client

        return create_vellum_client()

    @cached_property
    def parent_context(self) -> Optional[ParentContext]:
        if self._parent_context:
            return self._parent_context
        return None

    def _emit_subworkflow_event(self, event: "WorkflowEvent") -> None:
        if self._event_queue:
            self._event_queue.put(event)

    def _register_event_queue(self, event_queue: Queue["WorkflowEvent"]) -> None:
        self._event_queue = event_queue
