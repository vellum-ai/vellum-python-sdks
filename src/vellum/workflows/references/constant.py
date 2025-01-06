from typing import TYPE_CHECKING, Generic, TypeVar

from vellum.workflows.descriptors.base import BaseDescriptor

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class ConstantValueReference(BaseDescriptor[_T], Generic[_T]):
    def __init__(
        self,
        value: _T,
    ) -> None:
        self._value = value
        types = (type(self._value),)
        super().__init__(name=str(self._value), types=types)

    def resolve(self, state: "BaseState") -> _T:
        return self._value
