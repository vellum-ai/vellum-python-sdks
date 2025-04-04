import time
from typing import Callable, Generic, Optional, Type

from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.workflow import is_terminal_workflow_execution_event
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import create_adornment
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.generics import StateType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


class RetryNode(BaseAdornmentNode[StateType], Generic[StateType]):
    """
    Used to retry a Subworkflow a specified number of times.

    max_attempts: int - The maximum number of attempts to retry the Subworkflow
    delay: float = None - The number of seconds to wait between retries
    retry_on_error_code: Optional[WorkflowErrorCode] = None - The error code to retry on
    retry_on_condition: Optional[BaseDescriptor] = None - The condition to retry on
    subworkflow: Type["BaseWorkflow"] - The Subworkflow to execute
    """

    max_attempts: int
    delay: Optional[float] = None
    retry_on_error_code: Optional[WorkflowErrorCode] = None
    retry_on_condition: Optional[BaseDescriptor] = None

    class SubworkflowInputs(BaseInputs):
        attempt_number: int

    def run(self) -> BaseNode.Outputs:
        if self.max_attempts <= 0:
            raise Exception("max_attempts must be greater than 0")

        for index in range(self.max_attempts):
            attempt_number = index + 1
            parent_context = get_parent_context()
            with execution_context(parent_context=parent_context):
                subworkflow = self.subworkflow(
                    parent_state=self.state,
                    context=WorkflowContext(
                        vellum_client=self._context.vellum_client, generated_files=self._context.generated_files
                    ),
                )
                subworkflow_stream = subworkflow.stream(
                    inputs=self.SubworkflowInputs(attempt_number=attempt_number),
                    event_filter=all_workflow_event_filter,
                    node_output_mocks=self._context._get_all_node_output_mocks(),
                )

            node_outputs: Optional[BaseNode.Outputs] = None
            exception: Optional[NodeException] = None
            for event in subworkflow_stream:
                self._context._emit_subworkflow_event(event)

                if not is_terminal_workflow_execution_event(event):
                    continue

                if event.workflow_definition != self.subworkflow:
                    continue

                if event.name == "workflow.execution.fulfilled":
                    node_outputs = self.Outputs()

                    for output_descriptor, output_value in event.outputs:
                        setattr(node_outputs, output_descriptor.name, output_value)
                elif event.name == "workflow.execution.paused":
                    exception = NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"Subworkflow unexpectedly paused on attempt {attempt_number}",
                    )
                elif self.retry_on_error_code and self.retry_on_error_code != event.error.code:
                    exception = NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"""Unexpected rejection on attempt {attempt_number}: {event.error.code.value}.
Message: {event.error.message}""",
                    )
                elif self.retry_on_condition and not resolve_value(self.retry_on_condition, self.state):
                    exception = NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"""Rejection failed on attempt {attempt_number}: {event.error.code.value}.
Message: {event.error.message}""",
                    )
                else:
                    last_exception = NodeException(
                        event.error.message,
                        code=event.error.code,
                    )
                    if self.delay:
                        time.sleep(self.delay)

            if exception:
                raise exception

            if node_outputs:
                return node_outputs

        raise last_exception

    @classmethod
    def wrap(
        cls,
        max_attempts: int = 3,
        delay: Optional[float] = None,
        retry_on_error_code: Optional[WorkflowErrorCode] = None,
        retry_on_condition: Optional[BaseDescriptor] = None,
    ) -> Callable[..., Type["RetryNode"]]:
        return create_adornment(
            cls,
            attributes={
                "max_attempts": max_attempts,
                "delay": delay,
                "retry_on_error_code": retry_on_error_code,
                "retry_on_condition": retry_on_condition,
            },
        )
