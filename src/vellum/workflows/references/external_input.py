from typing import TYPE_CHECKING, Any, Generic, Optional, Tuple, Type, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

if TYPE_CHECKING:
    from vellum.workflows.inputs.base import BaseInputs
    from vellum.workflows.state.base import BaseState

_InputType = TypeVar("_InputType")


class ExternalInputReference(BaseDescriptor[_InputType], Generic[_InputType]):

    def __init__(
        self,
        *,
        name: str,
        types: Tuple[Type[_InputType], ...],
        instance: Optional[_InputType],
        inputs_class: Type["BaseInputs"],
    ) -> None:
        super().__init__(name=name, types=types, instance=instance)
        self._inputs_class = inputs_class

    @property
    def inputs_class(self) -> Type["BaseInputs"]:
        return self._inputs_class

    def resolve(self, state: "BaseState") -> _InputType:
        external_input = state.meta.external_inputs.get(self)
        if external_input is not undefined:
            return cast(_InputType, external_input)

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        raise NodeException(f"Missing required Node Input: {self._name}", code=WorkflowErrorCode.INVALID_INPUTS)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        # Check equality of the name
        base_equal = super().__eq__(other)
        if not base_equal:
            return False

        return self._inputs_class == other._inputs_class

    def __hash__(self) -> int:
        return hash((self._name, self._inputs_class))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
