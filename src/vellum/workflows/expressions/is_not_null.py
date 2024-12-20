from typing import Generic, TypeVar, Union

from vellum.workflows.constants import UNDEF
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class IsNotNullExpression(BaseDescriptor[bool], Generic[_T]):
    def __init__(
        self,
        *,
        expression: Union[BaseDescriptor[_T], _T],
    ) -> None:
        super().__init__(name=f"{expression} is not None", types=(bool,))
        self._expression = expression

    def resolve(self, state: "BaseState") -> bool:
        expression = resolve_value(self._expression, state)
        return expression is not None and expression is not UNDEF
