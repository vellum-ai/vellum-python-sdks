from typing import Any, Generic, Protocol, TypeVar, Union, runtime_checkable
from typing_extensions import TypeGuard

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState


@runtime_checkable
class SupportsGreaterThan(Protocol):
    def __gt__(self, other: Any) -> bool: ...


def has_gt(obj: Any) -> TypeGuard[SupportsGreaterThan]:
    return hasattr(obj, "__gt__")


LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class GreaterThanExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} > {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        lhs = resolve_value(self._lhs, state)
        rhs = resolve_value(self._rhs, state)

        if not has_gt(lhs):
            raise InvalidExpressionException(f"'{lhs.__class__.__name__}' must support the '>' operator")

        return lhs > rhs
