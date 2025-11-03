import logging
from uuid import UUID
from typing import Iterator, Optional, Type, Union

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.nodes.utils import cast_to_output_type
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.resolvers.types import LoadStateResult
from vellum.workflows.state.base import BaseState

logger = logging.getLogger(__name__)


class VellumResolver(BaseWorkflowResolver):
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        return iter([])

    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        return iter([])

    def _deserialize_state(self, state_data: dict, state_class: Type[BaseState]) -> BaseState:
        """Deserialize state data with proper type conversion for complex types like List[ChatMessage]."""
        converted_data = {}

        annotations = getattr(state_class, "__annotations__", {})

        for field_name, field_value in state_data.items():
            if field_name in annotations:
                field_type = annotations[field_name]
                converted_data[field_name] = cast_to_output_type(field_value, field_type)
            else:
                converted_data[field_name] = field_value

        return state_class(**converted_data)

    def load_state(self, previous_execution_id: Optional[Union[UUID, str]] = None) -> Optional[LoadStateResult]:
        if isinstance(previous_execution_id, UUID):
            previous_execution_id = str(previous_execution_id)

        if previous_execution_id is None:
            return None

        if not self._context:
            logger.warning("Cannot load state: No workflow context registered")
            return None

        client = self._context.vellum_client
        response = client.workflows.retrieve_state(
            span_id=previous_execution_id,
        )

        if response.state is None:
            return None

        if "meta" in response.state:
            response.state.pop("meta")

        if self._workflow_class:
            state_class = self._workflow_class.get_state_class()
            state = self._deserialize_state(response.state, state_class)
        else:
            logger.warning("No workflow class registered, falling back to BaseState")
            state = BaseState(**response.state)

        if (
            response.previous_trace_id is None
            or response.root_trace_id is None
            or response.previous_span_id is None
            or response.root_span_id is None
        ):
            return LoadStateResult(
                state=state,
                previous_trace_id=response.trace_id,
                previous_span_id=response.span_id,
                root_trace_id=response.trace_id,
                root_span_id=response.span_id,
            )

        return LoadStateResult(
            state=state,
            previous_trace_id=response.previous_trace_id,
            previous_span_id=response.previous_span_id,
            root_trace_id=response.root_trace_id,
            root_span_id=response.root_span_id,
        )
