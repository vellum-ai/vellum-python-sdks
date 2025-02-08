from typing import Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

_V = TypeVar("_V")
_S = TypeVar("_S")
_E = TypeVar("_E")


class NotBetweenExpression(BaseDescriptor[bool], Generic[_V, _S, _E]):
    def __init__(
        self,
        *,
        value: Union[BaseDescriptor[_V], _V],
        start: Union[BaseDescriptor[_S], _S],
        end: Union[BaseDescriptor[_E], _E],
    ) -> None:
        super().__init__(name=f"{value} is not between {start} and {end}", types=(bool,))
        self._value = value
        self._start = start
        self._end = end

    def resolve(self, state: "BaseState") -> bool:
        value = resolve_value(self._value, state)
        if not isinstance(value, (int, float)):
            raise InvalidExpressionException(f"Expected a numeric value, got: {value.__class__.__name__}")

        start = resolve_value(self._start, state)
        if not isinstance(start, (int, float)):
            raise InvalidExpressionException(f"Expected a numeric start value, got: {start.__class__.__name__}")

        end = resolve_value(self._end, state)
        if not isinstance(end, (int, float)):
            raise InvalidExpressionException(f"Expected a numeric end value, got: {end.__class__.__name__}")

        return value < start or value > end
