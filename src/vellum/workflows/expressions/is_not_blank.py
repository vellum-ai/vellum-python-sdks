from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class IsNotBlankExpression(BaseDescriptor[bool], Generic[_T]):
    def __init__(
        self,
        *,
        expression: Union[BaseDescriptor[_T], _T],
    ) -> None:
        super().__init__(name=f"{expression} is not blank", types=(bool,))
        self._expression = expression

    def resolve(self, state: "BaseState") -> bool:
        expression = resolve_value(self._expression, state)
        if not isinstance(expression, str):
            raise InvalidExpressionException(f"Expected a string expression, got: {expression.__class__.__name__}")

        return len(expression) != 0
