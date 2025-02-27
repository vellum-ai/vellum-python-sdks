from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class LessThanExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} < {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        lhs = resolve_value(self._lhs, state)
        rhs = resolve_value(self._rhs, state)

        try:
            return lhs < rhs  # type: ignore[operator]
        except TypeError:
            raise InvalidExpressionException(f"Cannot compare '{lhs.__class__.__name__}' < '{rhs.__class__.__name__}'")
