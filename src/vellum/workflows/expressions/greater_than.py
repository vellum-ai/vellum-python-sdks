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


def _try_parse_numeric_string(value: Any) -> Any:
    """
    Attempt to parse a string value as a number (int or float).

    This is to support the legacy workflow runner logic where string operands
    should be automatically parsed as numbers when compared with numeric types.

    Returns the parsed number if successful, otherwise returns the original value.
    """
    if not isinstance(value, str):
        return value

    try:
        if "." not in value:
            return int(value)
        return float(value)
    except (ValueError, TypeError):
        return value


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

        # Parse string operands as numbers when comparing with numeric types
        if isinstance(lhs, str) and isinstance(rhs, (int, float)):
            lhs = _try_parse_numeric_string(lhs)
        elif isinstance(rhs, str) and isinstance(lhs, (int, float)):
            rhs = _try_parse_numeric_string(rhs)

        if not has_gt(lhs):
            raise InvalidExpressionException(f"'{lhs.__class__.__name__}' must support the '>' operator")

        try:
            return lhs > rhs
        except TypeError as e:
            raise InvalidExpressionException(str(e))
