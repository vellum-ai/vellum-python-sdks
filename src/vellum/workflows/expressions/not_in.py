from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class NotInExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} not in {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        # Support any type that implements the not in operator
        # https://app.shortcut.com/vellum/story/4658
        lhs = resolve_value(self._lhs, state)

        rhs = resolve_value(self._rhs, state)
        if not isinstance(rhs, (list, tuple, set, dict, str)):
            raise InvalidExpressionException(f"Expected a RHS that supported contains, got: {rhs.__class__.__name__}")

        return lhs not in rhs
