from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.errors.types import WorkflowError
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")
RHS = TypeVar("RHS")


class DoesNotContainExpression(BaseDescriptor[bool], Generic[LHS, RHS]):
    def __init__(
        self,
        *,
        lhs: Union[BaseDescriptor[LHS], LHS],
        rhs: Union[BaseDescriptor[RHS], RHS],
    ) -> None:
        super().__init__(name=f"{lhs} does not contain {rhs}", types=(bool,))
        self._lhs = lhs
        self._rhs = rhs

    def resolve(self, state: "BaseState") -> bool:
        # Support any type that implements the not in operator
        # https://app.shortcut.com/vellum/story/4658
        lhs = resolve_value(self._lhs, state)
        if not isinstance(lhs, (list, tuple, set, dict, str, WorkflowError)):
            raise InvalidExpressionException(
                f"Expected a LHS that supported `contains`, got `{lhs.__class__.__name__}`"
            )

        rhs = resolve_value(self._rhs, state)
        return rhs not in lhs
