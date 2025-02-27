import json
from typing import Any, Dict, Generic, TypeVar, Union

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

_T = TypeVar("_T")


class ParseJsonExpression(BaseDescriptor[Dict[str, Any]], Generic[_T]):
    def __init__(
        self,
        *,
        expression: Union[BaseDescriptor[_T], _T],
    ) -> None:
        super().__init__(name=f"parse_json({expression})", types=(dict,))
        self._expression = expression

    def resolve(self, state: "BaseState") -> Dict[str, Any]:
        value = resolve_value(self._expression, state)

        if not isinstance(value, str):
            raise InvalidExpressionException(f"Expected a string, but got {value} of type {type(value)}")

        try:
            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                raise InvalidExpressionException(
                    f"Expected JSON to parse to a dictionary, but got {type(parsed).__name__}"
                )
            return parsed
        except json.JSONDecodeError:
            raise InvalidExpressionException(f"Failed to parse JSON: {value}")
