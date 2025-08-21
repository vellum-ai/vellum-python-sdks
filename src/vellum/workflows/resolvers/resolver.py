import logging
from uuid import UUID
from typing import Iterator, Optional

from vellum.workflows.events.workflow import WorkflowEvent
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.state.base import BaseState, StateMeta

logger = logging.getLogger(__name__)


class VellumResolver(BaseWorkflowResolver):
    def get_latest_execution_events(self) -> Iterator[WorkflowEvent]:
        return iter([])

    def get_state_snapshot_history(self) -> Iterator[BaseState]:
        return iter([])

    def load_state(self, previous_execution_id: Optional[UUID] = None) -> Optional[BaseState]:
        if previous_execution_id is None:
            return None

        if not self._context:
            logger.warning("Cannot load state: No workflow context registered")
            return None

        client = self._context.vellum_client
        response = client.workflow_executions.retrieve_workflow_execution_detail(
            execution_id=str(previous_execution_id),
        )

        if response.state is None:
            return None

        meta = StateMeta.model_validate(response.state.pop("meta"))
        return BaseState(**response.state, meta=meta)
