from typing import TYPE_CHECKING, Any, Generic, Optional, Tuple, Type, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.constants import UNDEF
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import VellumErrorCode
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
        if external_input is not UNDEF:
            return cast(_InputType, external_input)

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        raise NodeException(f"Missing required Node Input: {self._name}", code=VellumErrorCode.INVALID_INPUTS)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
