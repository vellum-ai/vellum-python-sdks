from functools import cached_property
from uuid import UUID
from typing import TYPE_CHECKING, Generic, Optional, Tuple, Type, TypeVar, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.types.generics import import_workflow_class
from vellum.workflows.utils.uuids import get_workflow_input_id

if TYPE_CHECKING:
    from vellum.workflows.inputs.base import BaseInputs
    from vellum.workflows.state.base import BaseState

_InputType = TypeVar("_InputType")


class WorkflowInputReference(BaseDescriptor[_InputType], Generic[_InputType]):

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

    @cached_property
    def id(self) -> UUID:
        """Generate deterministic UUID from inputs class and input name."""
        return get_workflow_input_id(self._inputs_class, self.name)

    def _coerce_to_declared_type(self, value: _InputType) -> _InputType:
        """Coerce value to the declared type if needed.

        This handles cases where the API returns a float for an int field
        (since NumberVellumValue.value is typed as float).
        """
        if not self.types:
            return value

        expected_type = self.types[0]
        if expected_type is int and isinstance(value, float):
            if value.is_integer():
                return cast(_InputType, int(value))
            raise NodeException(
                f"Expected integer for input '{self._name}', but received non-integer float: {value}",
                code=WorkflowErrorCode.INVALID_INPUTS,
            )

        return value

    def resolve(self, state: "BaseState") -> _InputType:
        if hasattr(state.meta.workflow_inputs, self._name) and (
            state.meta.workflow_definition == self._inputs_class.__parent_class__
            or not issubclass(self._inputs_class.__parent_class__, import_workflow_class())
        ):
            value = getattr(state.meta.workflow_inputs, self._name)
            return cast(_InputType, self._coerce_to_declared_type(value))

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        if type(None) in self.types:
            return cast(_InputType, None)

        raise NodeException(f"Missing required Workflow input: {self._name}", code=WorkflowErrorCode.INVALID_INPUTS)

    def __repr__(self) -> str:
        return f"{self._inputs_class.__qualname__}.{self.name}"
