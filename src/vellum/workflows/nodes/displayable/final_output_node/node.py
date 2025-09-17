from typing import Any, Dict, Generic, Tuple, Type, TypeVar, get_args

from vellum.workflows.constants import undefined
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.bases.base import BaseNodeMeta
from vellum.workflows.nodes.utils import cast_to_output_type
from vellum.workflows.ports import NodePorts
from vellum.workflows.references.output import OutputReference
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

    def __validate__(cls) -> None:
        cls._validate_output_type_consistency(cls)

    @classmethod
    def _validate_output_type_consistency(mcs, cls: Type) -> None:
        """
        Validates that the declared output type of FinalOutputNode matches
        the type of the descriptor assigned to the 'value' attribute in its Outputs class.

        Raises ValueError if there's a type mismatch.
        """
        if not hasattr(cls, "Outputs"):
            return

        outputs_class = cls.Outputs
        if not hasattr(outputs_class, "value"):
            return

        declared_output_type = cls.get_output_type()
        value_descriptor = None

        if "value" in outputs_class.__dict__:
            value_descriptor = outputs_class.__dict__["value"]
        else:
            value_descriptor = getattr(outputs_class, "value")

        if isinstance(value_descriptor, OutputReference):
            descriptor_types = value_descriptor.types

            type_mismatch = True
            for descriptor_type in descriptor_types:
                if descriptor_type == declared_output_type:
                    type_mismatch = False
                    break
                try:
                    if issubclass(descriptor_type, declared_output_type) or issubclass(
                        declared_output_type, descriptor_type
                    ):
                        type_mismatch = False
                        break
                except TypeError:
                    # Handle cases where types aren't classes (e.g., Union)
                    if str(descriptor_type) == str(declared_output_type):
                        type_mismatch = False
                        break

            if type_mismatch:
                declared_type_name = getattr(declared_output_type, "__name__", str(declared_output_type))
                descriptor_type_names = [getattr(t, "__name__", str(t)) for t in descriptor_types]

                raise ValueError(
                    f"Output type mismatch in {cls.__name__}: "
                    f"FinalOutputNode is declared with output type '{declared_type_name}' "
                    f"but the 'value' descriptor has type(s) {descriptor_type_names}. "
                    f"The output descriptor type must match the declared FinalOutputNode output type."
                )


class FinalOutputNode(BaseNode[StateType], Generic[StateType, _OutputType], metaclass=_FinalOutputNodeMeta):
    """
    Used to directly reference the output of another node.
    This provides backward compatibility with Vellum's Final Output Node.
    """

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY

    class Ports(NodePorts):
        pass

    class Outputs(BaseNode.Outputs):
        # We use our mypy plugin to override the _OutputType with the actual output type
        # for downstream references to this output.
        value: _OutputType = undefined  # type: ignore[valid-type]

    def run(self) -> Outputs:
        original_outputs = self.Outputs()

        return self.Outputs(
            value=cast_to_output_type(
                original_outputs.value,
                self.__class__.get_output_type(),
            )
        )

    __simulates_workflow_output__ = True
