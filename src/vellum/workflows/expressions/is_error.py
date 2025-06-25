from typing import Generic, TypeVar, Union

from vellum.client.types.vellum_error import VellumError
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.errors.types import WorkflowError
from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class IsErrorExpression(BaseDescriptor[bool], Generic[_T]):
    def __init__(
        self,
        *,
        expression: Union[BaseDescriptor[_T], _T],
    ) -> None:
        super().__init__(name=f"{expression} is error", types=(bool,))
        self._expression = expression

    def resolve(self, state: "BaseState") -> bool:
        expression = resolve_value(self._expression, state)
        return isinstance(expression, (VellumError, WorkflowError))
