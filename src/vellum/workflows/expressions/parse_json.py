import json
from typing import Any, Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class ParseJsonExpression(BaseDescriptor[Any], Generic[_T]):
    def __init__(
        self,
        *,
        expression: Union[BaseDescriptor[_T], _T],
    ) -> None:
        super().__init__(name=f"parse_json({expression})", types=(Any,))  # type: ignore[arg-type]
        self._expression = expression

    def resolve(self, state: "BaseState") -> Any:
        value = resolve_value(self._expression, state)

        if not isinstance(value, (str, bytes, bytearray)):
            raise InvalidExpressionException(f"Expected a string, but got {value} of type {type(value)}")

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise InvalidExpressionException(f"Failed to parse JSON: {e}") from e
