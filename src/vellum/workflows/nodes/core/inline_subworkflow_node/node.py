from typing import TYPE_CHECKING, Any, ClassVar, Dict, Generic, Iterator, Optional, Set, Tuple, Type, TypeVar, Union

from vellum.workflows.constants import undefined
from vellum.workflows.context import execution_context, get_parent_context
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.events.workflow import is_workflow_event
from vellum.workflows.exceptions import NodeException, WorkflowInitializationException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode, BaseNodeMeta
from vellum.workflows.outputs.base import BaseOutput, BaseOutputs
from vellum.workflows.references import OutputReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.types.core import EntityInputsInterface
from vellum.workflows.types.generics import InputsType, StateType
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

if TYPE_CHECKING:
    from vellum.workflows.workflows.base import BaseWorkflow

InnerStateType = TypeVar("InnerStateType", bound=BaseState)


class _InlineSubworkflowNodeMeta(BaseNodeMeta):
    def __new__(cls, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        node_class = super().__new__(cls, name, bases, dct)

        subworkflow_attribute = dct.get("subworkflow")
        if not subworkflow_attribute:
            return node_class

        if not issubclass(node_class, InlineSubworkflowNode):
            raise ValueError("_InlineSubworkflowNodeMeta can only be used on subclasses of InlineSubworkflowNode")

        subworkflow_outputs = getattr(subworkflow_attribute, "Outputs")
        if not issubclass(subworkflow_outputs, BaseOutputs):
            raise ValueError("subworkflow.Outputs must be a subclass of BaseOutputs")

        outputs_class = dct.get("Outputs")
        if not outputs_class:
            raise ValueError("Outputs class not found in base classes")

        if not issubclass(outputs_class, BaseNode.Outputs):
            raise ValueError("Outputs class must be a subclass of BaseNode.Outputs")

        for descriptor in subworkflow_outputs:
            node_class.__annotate_outputs_class__(outputs_class, descriptor)

        return node_class

    def __getattribute__(cls, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name != "__wrapped_node__" and issubclass(cls, InlineSubworkflowNode):
                return getattr(cls.__wrapped_node__, name)
            raise


class InlineSubworkflowNode(
    BaseNode[StateType], Generic[StateType, InputsType, InnerStateType], metaclass=_InlineSubworkflowNodeMeta
):
    """
    Used to execute a Subworkflow defined inline.

    subworkflow: Type["BaseWorkflow[InputsType, InnerStateType]"] - The Subworkflow to execute
    subworkflow_inputs: ClassVar[EntityInputsInterface] = {}
    """

    subworkflow: Type["BaseWorkflow[InputsType, InnerStateType]"]
    subworkflow_inputs: ClassVar[Union[EntityInputsInterface, BaseInputs, Type[undefined]]] = undefined

    def run(self) -> Iterator[BaseOutput]:
        with execution_context(parent_context=get_parent_context()):
            subworkflow = self.subworkflow(
                parent_state=self.state,
                context=WorkflowContext(
                    vellum_client=self._context.vellum_client, generated_files=self._context.generated_files
                ),
            )
            subworkflow_stream = subworkflow.stream(
                inputs=self._compile_subworkflow_inputs(),
                event_filter=all_workflow_event_filter,
                node_output_mocks=self._context._get_all_node_output_mocks(),
            )

        outputs: Optional[BaseOutputs] = None
        fulfilled_output_names: Set[str] = set()

        for event in subworkflow_stream:
            self._context._emit_subworkflow_event(event)

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

    def _compile_subworkflow_inputs(self) -> InputsType:
        inputs_class = self.subworkflow.get_inputs_class()
        try:
            if self.subworkflow_inputs is undefined:
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
        except WorkflowInitializationException as e:
            raise NodeException(message=str(e), code=e.code)

    @classmethod
    def __annotate_outputs_class__(cls, outputs_class: Type[BaseOutputs], reference: OutputReference) -> None:
        # Subclasses of InlineSubworkflowNode can override this method to provider their own
        # approach to annotating the outputs class based on the `subworkflow.Outputs`
        setattr(outputs_class, reference.name, reference)

        if cls.__output_ids__ is None:
            cls.__output_ids__ = {}

        cls.__output_ids__[reference.name] = uuid4_from_hash(f"{cls.__id__}|{reference.name}")
