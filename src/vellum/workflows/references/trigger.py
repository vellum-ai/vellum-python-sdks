"""Descriptor for referring to trigger attributes in workflow graphs."""

from __future__ import annotations

from uuid import UUID
from typing import TYPE_CHECKING, Any, Generic, Optional, Tuple, Type, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.client.types import StringChatMessageContent
from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException

if TYPE_CHECKING:
    from vellum.workflows.state.base import BaseState
    from vellum.workflows.triggers.base import BaseTrigger

_T = TypeVar("_T")


class TriggerAttributeReference(BaseDescriptor[_T], Generic[_T]):
    """Reference to a trigger attribute defined via type annotations."""

    def __init__(
        self,
        *,
        name: str,
        types: Tuple[Type[_T], ...],
        instance: Optional[_T],
        trigger_class: Type[BaseTrigger],
    ) -> None:
        super().__init__(name=name, types=types, instance=instance)
        self._trigger_class = trigger_class

    @property
    def trigger_class(self) -> Type[BaseTrigger]:
        return self._trigger_class

    @property
    def id(self) -> UUID:
        """
        Get the trigger attribute ID via the trigger class, which knows how to read
        metadata.json and fall back to hash-based IDs.

        This ensures trigger attribute IDs remain stable across serialization round-trips
        when metadata.json is present.
        """
        return self._trigger_class.get_attribute_id(self.name)

    def resolve(self, state: BaseState, expected_types: Optional[Tuple[Type[Any], ...]] = None) -> _T:
        trigger_attributes = state.meta.trigger_attributes or {}
        if self in trigger_attributes:
            value = trigger_attributes[self]
            return cast(_T, self._coerce_value(value, expected_types))

        if state.meta.parent:
            return self.resolve(state.meta.parent, expected_types)

        if type(None) in self.types:
            return cast(_T, None)

        raise NodeException(
            message=f"Missing trigger attribute '{self.name}' for {self._trigger_class.__name__}",
            code=WorkflowErrorCode.INVALID_INPUTS,
        )

    def _coerce_value(self, value: Any, expected_types: Optional[Tuple[Type[Any], ...]] = None) -> Any:
        """
        Coerce the resolved value to match expected types when possible.

        If the value is a list with a single StringChatMessageContent and the expected type is
        exactly str (and nothing else), extract and return the string value.
        """
        if expected_types is None:
            return value

        # Only coerce if str is the ONLY expected type
        if expected_types == (str,):
            if isinstance(value, list) and len(value) == 1:
                item = value[0]
                if isinstance(item, StringChatMessageContent):
                    return item.value

        return value

    def __repr__(self) -> str:
        return f"{self._trigger_class.__qualname__}.{self.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TriggerAttributeReference):
            return False
        return super().__eq__(other) and self._trigger_class == other._trigger_class

    def __hash__(self) -> int:
        return hash((self._trigger_class, self._name))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(cls)
