import logging
from uuid import UUID
from typing import Iterator, Optional, Tuple

from vellum.client.types.workflow_execution_initiated_event import WorkflowExecutionInitiatedEvent
from vellum.client.types.workflow_execution_span import WorkflowExecutionSpan
from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.resolvers.types import LoadStateResult, SpanLinkInfo
from vellum.workflows.state.base import BaseState, StateMeta

logger = logging.getLogger(__name__)


class VellumResolver(BaseWorkflowResolver):
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        return iter([])

    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        return iter([])

    def _find_execution_events(
        self, execution_id: UUID, spans: list
    ) -> Tuple[WorkflowExecutionInitiatedEvent, WorkflowExecutionInitiatedEvent]:
        previous_invocation: Optional[WorkflowExecutionInitiatedEvent] = None
        root_invocation: Optional[WorkflowExecutionInitiatedEvent] = None

        for span in spans:
            # Look for workflow execution spans
            if isinstance(span, WorkflowExecutionSpan):
                # Find the WorkflowExecutionInitiatedEvent in the span's events
                for event in span.events:
                    if isinstance(event, WorkflowExecutionInitiatedEvent):
                        # Check if this is the previous execution matches the execution_id
                        if event.span_id == str(execution_id):
                            previous_invocation = event

                        if not event.links:
                            root_invocation = event

                        if previous_invocation and root_invocation:
                            break

        return previous_invocation, root_invocation

    def load_state(self, previous_execution_id: Optional[UUID] = None) -> LoadStateResult:
        if previous_execution_id is None:
            return LoadStateResult(state=None, span_link_info=None)

        if not self._context:
            logger.warning("Cannot load state: No workflow context registered")
            return LoadStateResult(state=None, span_link_info=None)

        client = self._context.vellum_client
        response = client.workflow_executions.retrieve_workflow_execution_detail(
            execution_id=str(previous_execution_id),
        )

        if response.state is None:
            return LoadStateResult(state=None, span_link_info=None)

        previous_invocation, root_invocation = self._find_execution_events(previous_execution_id, response.spans)
        span_link_info = SpanLinkInfo(
            previous_trace_id=previous_invocation.trace_id,
            previous_span_id=previous_invocation.span_id,
            root_trace_id=root_invocation.trace_id,
            root_span_id=root_invocation.span_id,
        )

        meta = StateMeta.model_validate(response.state.pop("meta"))

        if self._workflow_class:
            state_class = self._workflow_class.get_state_class()
            state = state_class(**response.state, meta=meta)
        else:
            logger.warning("No workflow class registered, falling back to BaseState")
            state = BaseState(**response.state, meta=meta)

        return LoadStateResult(state=state, span_link_info=span_link_info)
