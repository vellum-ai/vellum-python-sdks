from typing import Any, Dict, Generic, Tuple, Type, TypeVar, get_args

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base import BaseNodeMeta
from vellum.workflows.nodes.utils import cast_to_output_type
from vellum.workflows.types import MergeBehavior
from vellum.workflows.types.generics import StateType
from vellum.workflows.types.utils import get_original_base

_OutputType = TypeVar("_OutputType")


# TODO: Consolidate all dynamic output metaclasses
# https://app.shortcut.com/vellum/story/5533
class _FinalOutputNodeMeta(BaseNodeMeta):
    def __new__(mcs, name: str, bases: Tuple[Type, ...], dct: Dict[str, Any]) -> Any:
        parent = super().__new__(mcs, name, bases, dct)

        # We use the compiled class to infer the output type for the Outputs.value descriptor.
        if not isinstance(parent, _FinalOutputNodeMeta):
            raise ValueError("FinalOutputNode must be created with the FinalOutputNodeMeta metaclass")

        annotations = parent.__dict__["Outputs"].__annotations__
        parent.__dict__["Outputs"].__annotations__ = {
            **annotations,
            "value": parent.get_output_type(),
        }
        return parent

    def get_output_type(cls) -> Type:
        original_base = get_original_base(cls)
        all_args = get_args(original_base)

        if len(all_args) < 2 or isinstance(all_args[1], TypeVar):
            return str
        else:
            return all_args[1]


class FinalOutputNode(BaseNode[StateType], Generic[StateType, _OutputType], metaclass=_FinalOutputNodeMeta):
    """
    Used to directly reference the output of another node.
    This provides backward compatibility with Vellum's Final Output Node.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Outputs(BaseNode.Outputs):
        # We use our mypy plugin to override the _OutputType with the actual output type
        # for downstream references to this output.
        value: _OutputType  # type: ignore[valid-type]

    def run(self) -> Outputs:
        output_reference = self.Outputs.value
        if not output_reference.instance:
            raise NodeException(
                code=WorkflowErrorCode.INVALID_OUTPUTS,
                message=f"Must set the `value` Output on '{self.__class__.__name__}'.",
            )

        return self.Outputs(value=cast_to_output_type(output_reference.instance, self.__class__.get_output_type()))
