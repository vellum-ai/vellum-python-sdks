from typing import Any, Generic, Protocol, TypeVar, Union, runtime_checkable
from typing_extensions import TypeGuard

from vellum.workflows.constants import undefined
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState


@runtime_checkable
class SupportsLen(Protocol):
    def __len__(self) -> int: ...


def has_len(obj: Any) -> TypeGuard[SupportsLen]:
    return hasattr(obj, "__len__")


_T = TypeVar("_T")


class LengthExpression(BaseDescriptor[int], Generic[_T]):
    def __init__(
        self,
        *,
        expression: Union[BaseDescriptor[_T], _T],
    ) -> None:
        super().__init__(name=f"length({expression})", types=(int,))
        self._expression = expression

    def resolve(self, state: "BaseState") -> int:
        expression = resolve_value(self._expression, state)

        if expression is undefined:
            raise InvalidExpressionException("Cannot get length of undefined value")

        if not has_len(expression):
            raise InvalidExpressionException(
                f"Expected an object that supports `len()`, got `{expression.__class__.__name__}`"
            )

        try:
            return len(expression)
        except TypeError as e:
            raise InvalidExpressionException(f"Cannot get length of `{expression.__class__.__name__}`: {str(e)}")
