from typing import TYPE_CHECKING, Generic, Iterator, Optional, Set, Type, TypeVar

from vellum.workflows.errors.types import VellumErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base_subworkflow_node import BaseSubworkflowNode
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.generics import StateType, WorkflowInputsType

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow

InnerStateType = TypeVar("InnerStateType", bound=BaseState)


class InlineSubworkflowNode(BaseSubworkflowNode[StateType], Generic[StateType, WorkflowInputsType, InnerStateType]):
    """
    Used to execute a Subworkflow defined inline.

    subworkflow: Type["BaseWorkflow[WorkflowInputsType, InnerStateType]"] - The Subworkflow to execute
    """

    subworkflow: Type["BaseWorkflow[WorkflowInputsType, InnerStateType]"]

    def run(self) -> Iterator[BaseOutput]:
        subworkflow = self.subworkflow(
            parent_state=self.state,
            context=self._context,
        )
        subworkflow_stream = subworkflow.stream(
            inputs=self._compile_subworkflow_inputs(),
        )

        outputs: Optional[BaseOutputs] = None
        fulfilled_output_names: Set[str] = set()

        for event in subworkflow_stream:
            if event.name == "workflow.execution.streaming":
                if event.output.is_fulfilled:
                    fulfilled_output_names.add(event.output.name)
                yield event.output
            elif event.name == "workflow.execution.fulfilled":
                outputs = event.outputs
            elif event.name == "workflow.execution.rejected":
                error = event.error
                if error.code in VellumErrorCode._value2member_map_:
                    raise NodeException(
                        message=error.message,
                        code=VellumErrorCode(error.code),
                    )
                else:
                    raise NodeException(
                        message=error.message,
                        code=VellumErrorCode.INTERNAL_ERROR,
                    )

        if outputs is None:
            raise NodeException(
                message="Expected to receive outputs from Workflow Deployment",
                code=VellumErrorCode.INVALID_OUTPUTS,
            )

        # For any outputs somehow in our final fulfilled outputs array,
        # but not fulfilled by the stream.
        for output_descriptor, output_value in outputs:
            if output_descriptor.name not in fulfilled_output_names:
                yield BaseOutput(
                    name=output_descriptor.name,
                    value=output_value,
                )

    def _compile_subworkflow_inputs(self) -> WorkflowInputsType:
        inputs_class = self.subworkflow.get_inputs_class()
        return inputs_class(**self.subworkflow_inputs)
