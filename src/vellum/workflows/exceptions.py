from uuid import uuid4
from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Type

from vellum.workflows.errors import WorkflowError, WorkflowErrorCode

if TYPE_CHECKING:
    from vellum.workflows.events.stream import WorkflowEventGenerator
    from vellum.workflows.events.workflow import WorkflowEvent
    from vellum.workflows.inputs import BaseInputs
    from vellum.workflows.state import BaseState
    from vellum.workflows.workflows.base import BaseWorkflow


class NodeException(Exception):
    def __init__(
        self,
        message: str,
        code: WorkflowErrorCode = WorkflowErrorCode.INTERNAL_ERROR,
        raw_data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.raw_data = raw_data
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
            raw_data=self.raw_data,
        )

    @staticmethod
    def of(workflow_error: WorkflowError) -> "NodeException":
        return NodeException(message=workflow_error.message, code=workflow_error.code, raw_data=workflow_error.raw_data)


class WorkflowInitializationException(Exception):
    def __init__(self, message: str, code: WorkflowErrorCode = WorkflowErrorCode.INVALID_INPUTS):
        self.message = message
        self.code = code
        super().__init__(message)

    @property
    def error(self) -> WorkflowError:
        return WorkflowError(
            message=self.message,
            code=self.code,
        )

    def stream(
        self,
        workflow_definition: Type["BaseWorkflow"],
        inputs: Optional["BaseInputs"] = None,
        initial_state: Optional["BaseState"] = None,
    ) -> "WorkflowEventGenerator[WorkflowEvent]":
        """
        Stream a workflow initiated event followed by a workflow rejected event.

        Args:
            workflow_definition: The workflow class that this exception relates to
            inputs: Optional inputs for the workflow initiated event
            initial_state: Optional initial state for the workflow initiated event

        Returns:
            WorkflowEventGenerator yielding initiated and rejected events
        """
        from vellum.workflows.context import get_execution_context
        from vellum.workflows.events.stream import WorkflowEventGenerator
        from vellum.workflows.events.workflow import (
            WorkflowEvent,
            WorkflowExecutionInitiatedBody,
            WorkflowExecutionInitiatedEvent,
            WorkflowExecutionRejectedBody,
            WorkflowExecutionRejectedEvent,
        )

        execution_context = get_execution_context()
        span_id = uuid4()

        def _generate_events() -> Generator["WorkflowEvent", None, None]:
            initiated_event: "WorkflowEvent" = WorkflowExecutionInitiatedEvent(
                trace_id=execution_context.trace_id,
                span_id=span_id,
                body=WorkflowExecutionInitiatedBody(
                    workflow_definition=workflow_definition,
                    inputs=inputs or workflow_definition.get_inputs_class()(),
                    initial_state=initial_state,
                ),
                parent=execution_context.parent_context,
            )
            yield initiated_event

            rejected_event = WorkflowExecutionRejectedEvent(
                trace_id=execution_context.trace_id,
                span_id=span_id,
                body=WorkflowExecutionRejectedBody(
                    workflow_definition=workflow_definition,
                    error=self.error,
                ),
                parent=execution_context.parent_context,
            )
            yield rejected_event

        return WorkflowEventGenerator(_generate_events(), span_id)

    @staticmethod
    def of(workflow_error: WorkflowError) -> "WorkflowInitializationException":
        return WorkflowInitializationException(message=workflow_error.message, code=workflow_error.code)
