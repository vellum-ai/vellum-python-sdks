from collections.abc import Mapping
import dataclasses
from typing import Any, Sequence, Type, TypeVar, Union, get_args, get_origin

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
            types=self._infer_accessor_types(base, field),
            instance=None,
        )
        self._base = base
        self._field = field

    def _infer_accessor_types(self, base: BaseDescriptor[LHS], field: Union[str, int]) -> tuple[Type, ...]:
        """
        Infer the types for this accessor expression based on the base descriptor's types
        and the field being accessed.
        """
        if not base.types:
            return ()

        inferred_types = []

        for base_type in base.types:
            origin = get_origin(base_type)
            args = get_args(base_type)

            if isinstance(field, int) and origin in (list, tuple) and args:
                if origin is list:
                    inferred_types.append(args[0])
                elif origin is tuple and len(args) == 2 and args[1] is ...:
                    inferred_types.append(args[0])
                elif origin is tuple and len(args) > abs(field):
                    if field >= 0:
                        inferred_types.append(args[field])
                    else:
                        inferred_types.append(args[field])
            elif isinstance(field, str) and origin in (dict,) and len(args) >= 2:
                inferred_types.append(args[1])  # Value type from Dict[K, V]

        return tuple(set(inferred_types)) if inferred_types else ()

    def resolve(self, state: "BaseState") -> Any:
        base = resolve_value(self._base, state)

        if dataclasses.is_dataclass(base):
            if isinstance(self._field, int):
                raise InvalidExpressionException("Cannot access field by index on a dataclass")

            try:
                return getattr(base, self._field)
            except AttributeError:
                raise InvalidExpressionException(f"Field '{self._field}' not found on dataclass {type(base).__name__}")

        if isinstance(base, BaseModel):
            if isinstance(self._field, int):
                raise InvalidExpressionException("Cannot access field by index on a BaseModel")

            try:
                return getattr(base, self._field)
            except AttributeError:
                raise InvalidExpressionException(f"Field '{self._field}' not found on BaseModel {type(base).__name__}")

        if isinstance(base, Mapping):
            try:
                return base[self._field]
            except KeyError:
                raise InvalidExpressionException(f"Key '{self._field}' not found in mapping")

        if isinstance(base, Sequence):
            try:
                index = int(self._field)
                return base[index]
            except (IndexError, ValueError):
                if isinstance(self._field, int) or (isinstance(self._field, str) and self._field.lstrip("-").isdigit()):
                    raise InvalidExpressionException(
                        f"Index {self._field} is out of bounds for sequence of length {len(base)}"
                    )
                else:
                    raise InvalidExpressionException(f"Invalid index '{self._field}' for sequence access")

        raise InvalidExpressionException(f"Cannot get field {self._field} from {base}")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
