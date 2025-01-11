from functools import cached_property
from queue import Queue
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from vellum import Vellum
from vellum.workflows.events.types import ParentContext
from vellum.workflows.nodes.mocks import MockNodeExecution, MockNodeExecutionArg
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.references.constant import ConstantValueReference
from vellum.workflows.vellum_client import create_vellum_client

if TYPE_CHECKING:
    from vellum.workflows.events.workflow import WorkflowEvent


class WorkflowContext:
    def __init__(
        self,
        *,
        vellum_client: Optional[Vellum] = None,
        parent_context: Optional[ParentContext] = None,
    ):
        self._vellum_client = vellum_client
        self._parent_context = parent_context
        self._event_queue: Optional[Queue["WorkflowEvent"]] = None
        self._node_output_mocks_map: Dict[Type[BaseOutputs], List[MockNodeExecution]] = {}

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

    @cached_property
    def node_output_mocks_map(self) -> Dict[Type[BaseOutputs], List[MockNodeExecution]]:
        return self._node_output_mocks_map

    def _emit_subworkflow_event(self, event: "WorkflowEvent") -> None:
        if self._event_queue:
            self._event_queue.put(event)

    def _register_event_queue(self, event_queue: Queue["WorkflowEvent"]) -> None:
        self._event_queue = event_queue

    def _register_node_output_mocks(self, node_output_mocks: MockNodeExecutionArg) -> None:
        for mock in node_output_mocks:
            if isinstance(mock, MockNodeExecution):
                key = mock.then_outputs.__class__
                value = mock
            else:
                key = mock.__class__
                value = MockNodeExecution(
                    when_condition=ConstantValueReference(True),
                    then_outputs=mock,
                )

            if key not in self._node_output_mocks_map:
                self._node_output_mocks_map[key] = [value]
            else:
                self._node_output_mocks_map[key].append(value)

    def _get_all_node_output_mocks(self) -> List[MockNodeExecution]:
        return [mock for mocks in self._node_output_mocks_map.values() for mock in mocks]
