from typing import Any, Generic, Protocol, TypeVar, Union, runtime_checkable
from typing_extensions import TypeGuard

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.expressions.comparison_utils import prepare_comparison_operands
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


@runtime_checkable
class SupportsGreaterThanOrEqualTo(Protocol):
    def __ge__(self, other: Any) -> bool: ...


def has_ge(obj: Any) -> TypeGuard[SupportsGreaterThanOrEqualTo]:
    return hasattr(obj, "__ge__")


class GreaterThanOrEqualToExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} >= {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        lhs = resolve_value(self._lhs, state)
        rhs = resolve_value(self._rhs, state)

        # Parse string operands as numbers when comparing with numeric types
        lhs, rhs = prepare_comparison_operands(lhs, rhs)

        if not has_ge(lhs):
            raise InvalidExpressionException(f"'{lhs.__class__.__name__}' must support the '>=' operator")

        try:
            return lhs >= rhs
        except TypeError as e:
            raise InvalidExpressionException(str(e))
