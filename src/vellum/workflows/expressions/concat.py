from typing import Generic, Sequence, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class ConcatExpression(BaseDescriptor[list], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], Sequence[LHS]],
        rhs: Union[BaseDescriptor[RHS], Sequence[RHS]],
    ) -> None:
        super().__init__(name=f"{lhs} + {rhs}", types=(list,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> list:
        lval = resolve_value(self._lhs, state) or []
        rval = resolve_value(self._rhs, state) or []
        return list(lval) + list(rval)
