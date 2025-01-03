from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Optional, Tuple, Type

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base import BaseNodeMeta
from vellum.workflows.nodes.utils import create_adornment
from vellum.workflows.outputs.base import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.generics import StateType

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow


class _RetryNodeMeta(BaseNodeMeta):
    def __new__(cls, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        node_class = super().__new__(cls, name, bases, dct)

        subworkflow_attribute = dct.get("subworkflow")
        if not subworkflow_attribute:
            return node_class

        subworkflow_outputs = getattr(subworkflow_attribute, "Outputs")
        if not issubclass(subworkflow_outputs, BaseOutputs):
            raise ValueError("subworkflow.Outputs must be a subclass of BaseOutputs")

        outputs_class = dct.get("Outputs")
        if not outputs_class:
            raise ValueError("Outputs class not found in base classes")

        if not issubclass(outputs_class, BaseNode.Outputs):
            raise ValueError("Outputs class must be a subclass of BaseNode.Outputs")

        for descriptor in subworkflow_outputs:
            setattr(outputs_class, descriptor.name, descriptor)

        return node_class

    def __getattribute__(cls, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name != "__wrapped_node__" and issubclass(cls, RetryNode):
                return getattr(cls.__wrapped_node__, name)
            raise

    @property
    def _localns(cls) -> Dict[str, Any]:
        return {
            **super()._localns,
            "SubworkflowInputs": getattr(cls, "SubworkflowInputs"),
        }


class RetryNode(BaseNode[StateType], Generic[StateType], metaclass=_RetryNodeMeta):
    """
    Used to retry a Subworkflow a specified number of times.

    max_attempts: int - The maximum number of attempts to retry the Subworkflow
    retry_on_error_code: Optional[VellumErrorCode] = None - The error code to retry on
    subworkflow: Type["BaseWorkflow[SubworkflowInputs, BaseState]"] - The Subworkflow to execute
    """

    __wrapped_node__: Optional[Type["BaseNode"]] = None
    max_attempts: int
    retry_on_error_code: Optional[WorkflowErrorCode] = None
    subworkflow: Type["BaseWorkflow[SubworkflowInputs, BaseState]"]

    class SubworkflowInputs(BaseInputs):
        attempt_number: int

    def run(self) -> BaseNode.Outputs:
        last_exception = Exception("max_attempts must be greater than 0")
        for index in range(self.max_attempts):
            attempt_number = index + 1
            subworkflow = self.subworkflow(
                parent_state=self.state,
                context=self._context,
            )
            terminal_event = subworkflow.run(
                inputs=self.SubworkflowInputs(attempt_number=attempt_number),
            )
            if terminal_event.name == "workflow.execution.fulfilled":
                node_outputs = self.Outputs()
                workflow_output_vars = vars(terminal_event.outputs)

                for output_name in workflow_output_vars:
                    setattr(node_outputs, output_name, workflow_output_vars[output_name])

                return node_outputs
            elif terminal_event.name == "workflow.execution.paused":
                last_exception = NodeException(
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                    message=f"Subworkflow unexpectedly paused on attempt {attempt_number}",
                )
                break
            elif self.retry_on_error_code and self.retry_on_error_code != terminal_event.error.code:
                last_exception = NodeException(
                    code=WorkflowErrorCode.INVALID_OUTPUTS,
                    message=f"""Unexpected rejection on attempt {attempt_number}: {terminal_event.error.code.value}.
Message: {terminal_event.error.message}""",
                )
                break
            else:
                last_exception = Exception(terminal_event.error.message)

        raise last_exception

    @classmethod
    def wrap(
        cls, max_attempts: int, retry_on_error_code: Optional[WorkflowErrorCode] = None
    ) -> Callable[..., Type["RetryNode"]]:
        return create_adornment(
            cls, attributes={"max_attempts": max_attempts, "retry_on_error_code": retry_on_error_code}
        )
