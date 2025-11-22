from functools import cached_property
from uuid import UUID
from typing import TYPE_CHECKING, Optional, Tuple, Type, TypeVar, cast

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.utils.uuids import get_state_value_id

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState


_T = TypeVar("_T")


class StateValueReference(BaseDescriptor[_T]):

    def __init__(
        self,
        *,
        name: str,
        types: Tuple[Type[_T], ...],
        instance: Optional[_T],
        state_class: Type["BaseState"],
    ) -> None:
        super().__init__(name=name, types=types, instance=instance)
        self._state_class = state_class

    @property
    def state_class(self) -> Type["BaseState"]:
        return self._state_class

    @cached_property
    def id(self) -> UUID:
        """Generate deterministic UUID from state class and state value name."""
        return get_state_value_id(self._state_class, self.name)

    def resolve(self, state: "BaseState") -> _T:
        if hasattr(state, self._name):
            return cast(_T, getattr(state, self._name))

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        raise NodeException(f"Missing required Workflow state: {self._name}", code=WorkflowErrorCode.INVALID_STATE)
