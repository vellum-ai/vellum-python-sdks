from typing import TYPE_CHECKING, Generic, Optional, Tuple, Type, TypeVar, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

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

    def resolve(self, state: "BaseState") -> _InputType:
        if hasattr(state.meta.workflow_inputs, self._name):
            return cast(_InputType, getattr(state.meta.workflow_inputs, self._name))

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        if type(None) in self.types:
            return cast(_InputType, None)

        raise NodeException(f"Missing required Workflow input: {self._name}", code=WorkflowErrorCode.INVALID_INPUTS)

    def __repr__(self) -> str:
        return f"{self._inputs_class.__qualname__}.{self.name}"
