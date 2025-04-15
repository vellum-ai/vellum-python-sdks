from functools import cache
from typing import TYPE_CHECKING, Any, Type, TypeVar
from typing_extensions import TypeGuard

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


@cache
def _import_node_class() -> Type["BaseNode"]:
    """
    Helper function to help avoid circular imports.
    """

    from vellum.workflows.nodes import BaseNode

    return BaseNode


def import_workflow_class() -> Type["BaseWorkflow"]:
    """
    Helper function to help avoid circular imports.
    """

    from vellum.workflows.workflows import BaseWorkflow

    return BaseWorkflow


def is_node_class(obj: Any) -> TypeGuard[Type["BaseNode"]]:
    base_node_class = _import_node_class()
    return isinstance(obj, type) and issubclass(obj, base_node_class)


def is_workflow_class(obj: Any) -> TypeGuard[Type["BaseWorkflow"]]:
    base_workflow_class = import_workflow_class()
    return isinstance(obj, type) and issubclass(obj, base_workflow_class)
