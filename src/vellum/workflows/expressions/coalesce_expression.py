from typing import TypeVar, Union

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState
from vellum.workflows.types.utils import resolve_combined_types

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class CoalesceExpression(BaseDescriptor[Union[LHS, RHS]]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(
            name=f"{lhs} ?? {rhs}",
            types=resolve_combined_types(lhs, rhs),
            instance=None,
        )
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> Union[LHS, RHS]:
        lhs = resolve_value(self._lhs, state)
        if lhs is not undefined and lhs is not None:
            return lhs

        return resolve_value(self._rhs, state)

    @property
    def lhs(self) -> Union[BaseDescriptor[LHS], LHS]:
        return self._lhs

    @property
    def rhs(self) -> Union[BaseDescriptor[RHS], RHS]:
        return self._rhs
