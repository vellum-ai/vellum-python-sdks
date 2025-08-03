from typing import Any, Generic, Protocol, TypeVar, Union, runtime_checkable
from typing_extensions import TypeGuard

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState


@runtime_checkable
class SupportsAdd(Protocol):
    def __add__(self, other: Any) -> Any: ...


def has_add(obj: Any) -> TypeGuard[SupportsAdd]:
    return hasattr(obj, "__add__")


LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class AddExpression(BaseDescriptor[Any], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} + {rhs}", types=(object,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> Any:
        lhs = resolve_value(self._lhs, state)
        rhs = resolve_value(self._rhs, state)

        if not has_add(lhs):
            raise InvalidExpressionException(f"'{lhs.__class__.__name__}' must support the '+' operator")

        return lhs + rhs
