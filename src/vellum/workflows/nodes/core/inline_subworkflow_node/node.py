from typing import TYPE_CHECKING, ClassVar, Generic, Iterator, Optional, Set, Type, TypeVar, Union

from vellum.workflows.constants import UNDEF
from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.core import EntityInputsInterface
from vellum.workflows.types.generics import StateType, WorkflowInputsType
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow

InnerStateType = TypeVar("InnerStateType", bound=BaseState)


class InlineSubworkflowNode(BaseNode[StateType], Generic[StateType, WorkflowInputsType, InnerStateType]):
    """
    Used to execute a Subworkflow defined inline.

    subworkflow: Type["BaseWorkflow[WorkflowInputsType, InnerStateType]"] - The Subworkflow to execute
    subworkflow_inputs: ClassVar[EntityInputsInterface] = {}
    """

    subworkflow: Type["BaseWorkflow[WorkflowInputsType, InnerStateType]"]
    subworkflow_inputs: ClassVar[Union[EntityInputsInterface, BaseInputs, Type[UNDEF]]] = UNDEF

    def run(self) -> Iterator[BaseOutput]:
        with execution_context(parent_context=get_parent_context() or self._context.parent_context):
            subworkflow = self.subworkflow(
                parent_state=self.state,
                context=WorkflowContext(vellum_client=self._context.vellum_client),
            )
            subworkflow_stream = subworkflow.stream(
                inputs=self._compile_subworkflow_inputs(),
                event_filter=all_workflow_event_filter,
            )

        outputs: Optional[BaseOutputs] = None
        fulfilled_output_names: Set[str] = set()

        for event in subworkflow_stream:
            self._context._emit_subworkflow_event(event)
            if event.name == "workflow.execution.streaming":
                if event.output.is_fulfilled:
                    fulfilled_output_names.add(event.output.name)
                yield event.output
            elif event.name == "workflow.execution.fulfilled":
                outputs = event.outputs
            elif event.name == "workflow.execution.rejected":
                raise NodeException.of(event.error)

        if outputs is None:
            raise NodeException(
                message="Expected to receive outputs from Workflow Deployment",
                code=WorkflowErrorCode.INVALID_OUTPUTS,
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
        if self.subworkflow_inputs is UNDEF:
            inputs_dict = {}
            for descriptor in inputs_class:
                if hasattr(self, descriptor.name):
                    inputs_dict[descriptor.name] = getattr(self, descriptor.name)

            return inputs_class(**inputs_dict)
        elif isinstance(self.subworkflow_inputs, dict):
            return inputs_class(**self.subworkflow_inputs)
        elif isinstance(self.subworkflow_inputs, inputs_class):
            return self.subworkflow_inputs
        else:
            raise ValueError(f"Invalid subworkflow inputs type: {type(self.subworkflow_inputs)}")
