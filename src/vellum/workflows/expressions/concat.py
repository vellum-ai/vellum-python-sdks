from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class ConcatExpression(BaseDescriptor[list], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} + {rhs}", types=(list,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> list:
        lval = resolve_value(self._lhs, state)
        rval = resolve_value(self._rhs, state)

        if not isinstance(lval, list):
            raise InvalidExpressionException(f"Expected LHS to be a list, got {type(lval)}")
        if not isinstance(rval, list):
            raise InvalidExpressionException(f"Expected RHS to be a list, got {type(rval)}")

        return lval + rval
