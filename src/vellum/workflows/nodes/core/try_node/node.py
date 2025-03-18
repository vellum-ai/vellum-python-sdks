from typing import Callable, Generic, Iterator, Optional, Set, Type

from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.events.workflow import is_workflow_event
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base_adornment_node import BaseAdornmentNode
from vellum.workflows.nodes.utils import create_adornment
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.references.output import OutputReference
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.generics import StateType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


class TryNode(BaseAdornmentNode[StateType], Generic[StateType]):
    """
    Used to execute a Subworkflow and handle errors.

    on_error_code: Optional[WorkflowErrorCode] = None - The error code to handle
    subworkflow: Type["BaseWorkflow"] - The Subworkflow to execute
    """

    on_error_code: Optional[WorkflowErrorCode] = None

    class Outputs(BaseNode.Outputs):
        error: Optional[WorkflowError] = None

    def run(self) -> Iterator[BaseOutput]:
        parent_context = get_parent_context()
        with execution_context(parent_context=parent_context):
            subworkflow = self.subworkflow(
                parent_state=self.state,
                context=WorkflowContext(vellum_client=self._context.vellum_client),
            )
            subworkflow_stream = subworkflow.stream(
                event_filter=all_workflow_event_filter,
                node_output_mocks=self._context._get_all_node_output_mocks(),
            )

        outputs: Optional[BaseOutputs] = None
        exception: Optional[NodeException] = None
        fulfilled_output_names: Set[str] = set()

        for event in subworkflow_stream:
            self._context._emit_subworkflow_event(event)
            if exception:
                continue

            if not is_workflow_event(event):
                continue

            if event.workflow_definition != self.subworkflow:
                continue

            if event.name == "workflow.execution.streaming":
                if event.output.is_fulfilled:
                    fulfilled_output_names.add(event.output.name)
                yield event.output
            elif event.name == "workflow.execution.fulfilled":
                outputs = event.outputs
            elif event.name == "workflow.execution.paused":
                exception = NodeException(
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                    message="Subworkflow unexpectedly paused within Try Node",
                )
            elif event.name == "workflow.execution.rejected":
                if self.on_error_code and self.on_error_code != event.error.code:
                    exception = NodeException(
                        code=WorkflowErrorCode.INVALID_OUTPUTS,
                        message=f"""Unexpected rejection: {event.error.code.value}.
Message: {event.error.message}""",
                    )
                else:
                    outputs = self.Outputs(error=event.error)

        if exception:
            raise exception

        if outputs is None:
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message="Expected to receive outputs from Try Node's subworkflow",
            )

        # For any outputs somehow in our final fulfilled outputs array,
        # but not fulfilled by the stream.
        for descriptor, value in outputs:
            if descriptor.name not in fulfilled_output_names:
                yield BaseOutput(
                    name=descriptor.name,
                    value=value,
                )

    @classmethod
    def wrap(cls, on_error_code: Optional[WorkflowErrorCode] = None) -> Callable[..., Type["TryNode"]]:
        return create_adornment(cls, attributes={"on_error_code": on_error_code})

    @classmethod
    def __annotate_outputs_class__(cls, outputs_class: Type[BaseOutputs], reference: OutputReference) -> None:
        if reference.name == "error":
            raise ValueError("`error` is a reserved name for TryNode.Outputs")

        super().__annotate_outputs_class__(outputs_class, reference)
