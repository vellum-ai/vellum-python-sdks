import logging
from uuid import UUID
from typing import Iterator, List, Optional, Tuple, Union

from vellum.client.types.vellum_span import VellumSpan
from vellum.client.types.workflow_execution_initiated_event import WorkflowExecutionInitiatedEvent
from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.resolvers.types import LoadStateResult
from vellum.workflows.state.base import BaseState

logger = logging.getLogger(__name__)


class VellumResolver(BaseWorkflowResolver):
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        return iter([])

    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        return iter([])

    def _find_previous_and_root_span(
        self, execution_id: str, spans: List[VellumSpan]
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        previous_trace_id: Optional[str] = None
        root_trace_id: Optional[str] = None
        previous_span_id: Optional[str] = None
        root_span_id: Optional[str] = None

        for span in spans:
            # Look for workflow execution spans with matching ID first
            if span.name == "workflow.execution" and span.span_id == execution_id:
                # Find the WorkflowExecutionInitiatedEvent in the span's events
                initiated_event = next(
                    (event for event in span.events if isinstance(event, WorkflowExecutionInitiatedEvent)), None
                )
                if initiated_event:
                    previous_trace_id = initiated_event.trace_id
                    previous_span_id = initiated_event.span_id
                    links = initiated_event.links
                    if links:
                        root_span = next((link for link in links if link.type == "ROOT_SPAN"), None)
                        if root_span:
                            root_trace_id = root_span.trace_id
                            root_span_id = root_span.span_context.span_id
                    else:
                        # no links means this is the first execution
                        root_trace_id = initiated_event.trace_id
                        root_span_id = initiated_event.span_id
                    break

        return previous_trace_id, root_trace_id, previous_span_id, root_span_id

    def load_state(self, previous_execution_id: Optional[Union[UUID, str]] = None) -> Optional[LoadStateResult]:
        if isinstance(previous_execution_id, UUID):
            previous_execution_id = str(previous_execution_id)

        if previous_execution_id is None:
            return None

        if not self._context:
            logger.warning("Cannot load state: No workflow context registered")
            return None

        client = self._context.vellum_client
        response = client.workflow_executions.retrieve_workflow_execution_detail(
            execution_id=previous_execution_id,
        )

        if response.state is None:
            return None

        previous_trace_id, root_trace_id, previous_span_id, root_span_id = self._find_previous_and_root_span(
            previous_execution_id, response.spans
        )

        if previous_trace_id is None or root_trace_id is None or previous_span_id is None or root_span_id is None:
            logger.warning("Could not find required execution events for state loading")
            return None

        if "meta" in response.state:
            response.state.pop("meta")

        if self._workflow_class:
            state_class = self._workflow_class.get_state_class()
            state = state_class(**response.state)
        else:
            logger.warning("No workflow class registered, falling back to BaseState")
            state = BaseState(**response.state)

        return LoadStateResult(
            state=state,
            previous_trace_id=previous_trace_id,
            previous_span_id=previous_span_id,
            root_trace_id=root_trace_id,
            root_span_id=root_span_id,
        )
