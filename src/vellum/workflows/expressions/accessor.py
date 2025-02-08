from collections.abc import Mapping
import dataclasses
from typing import Any, Sequence, Type, TypeVar, Union

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.descriptors.exceptions import InvalidExpressionException
from vellum.workflows.descriptors.utils import resolve_value
from vellum.workflows.state.base import BaseState

LHS = TypeVar("LHS")


class AccessorExpression(BaseDescriptor[Any]):
    def __init__(
        self,
        *,
        base: BaseDescriptor[LHS],
        field: Union[str, int],
    ) -> None:
        super().__init__(
            name=f"{base.name}.{field}",
            types=(),
            instance=None,
        )
        self._base = base
        self._field = field

    def resolve(self, state: "BaseState") -> Any:
        base = resolve_value(self._base, state)

        if dataclasses.is_dataclass(base):
            if isinstance(self._field, int):
                raise InvalidExpressionException("Cannot access field by index on a dataclass")

            return getattr(base, self._field)

        if isinstance(base, BaseModel):
            if isinstance(self._field, int):
                raise InvalidExpressionException("Cannot access field by index on a BaseModel")

            return getattr(base, self._field)

        if isinstance(base, Mapping):
            return base[self._field]

        if isinstance(base, Sequence):
            index = int(self._field)
            return base[index]

        raise InvalidExpressionException(f"Cannot get field {self._field} from {base}")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
