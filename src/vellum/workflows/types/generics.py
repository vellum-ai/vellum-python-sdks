from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from vellum.workflows import BaseWorkflow
    from vellum.workflows.inputs import BaseInputs
    from vellum.workflows.nodes import BaseNode
    from vellum.workflows.outputs import BaseOutputs
    from vellum.workflows.state import BaseState

NodeType = TypeVar("NodeType", bound="BaseNode")
StateType = TypeVar("StateType", bound="BaseState")
WorkflowType = TypeVar("WorkflowType", bound="BaseWorkflow")
InputsType = TypeVar("InputsType", bound="BaseInputs")
OutputsType = TypeVar("OutputsType", bound="BaseOutputs")
