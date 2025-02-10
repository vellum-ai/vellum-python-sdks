from typing import Generic, TypeVar, Union

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.errors.types import WorkflowError
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class ContainsExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} contains {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        # Support any type that implements the in operator
        # https://app.shortcut.com/vellum/story/4658
        lhs = resolve_value(self._lhs, state)
        # assumes that lack of is also false
        if lhs is undefined:
            return False
        if not isinstance(lhs, (list, tuple, set, dict, str, WorkflowError)):
            raise InvalidExpressionException(
                f"Expected a LHS that supported `contains`, got `{lhs.__class__.__name__}`"
            )

        rhs = resolve_value(self._rhs, state)
        return rhs in lhs
