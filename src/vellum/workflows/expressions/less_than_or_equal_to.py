from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class LessThanOrEqualToExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} <= {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        # Support any type that implements the <= operator
        # https://app.shortcut.com/vellum/story/4658
        lhs = resolve_value(self._lhs, state)
        if not isinstance(lhs, (int, float)):
            raise InvalidExpressionException(f"Expected a numeric lhs value, got: {lhs.__class__.__name__}")

        rhs = resolve_value(self._rhs, state)
        if not isinstance(rhs, (int, float)):
            raise InvalidExpressionException(f"Expected a numeric rhs value, got: {rhs.__class__.__name__}")

        return lhs <= rhs
