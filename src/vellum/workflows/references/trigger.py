"""Descriptor for referring to trigger attributes in workflow graphs."""

from __future__ import annotations

from uuid import UUID
from typing import TYPE_CHECKING, Any, Generic, Optional, Tuple, Type, TypeVar, cast

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from vellum.workflows.descriptors.base import BaseDescriptor
from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.utils.trigger_metadata import get_trigger_attribute_id_from_metadata
from vellum.workflows.utils.uuids import get_trigger_attribute_id

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
        Get the trigger attribute ID, first checking metadata.json for a stable ID,
        then falling back to a deterministic hash-based ID.

        This ensures trigger attribute IDs remain stable across serialization round-trips
        when metadata.json is present.
        """
        # First try to get the ID from metadata.json
        metadata_id = get_trigger_attribute_id_from_metadata(self._trigger_class, self.name)
        if metadata_id is not None:
            return metadata_id

        # Fall back to deterministic hash-based ID
        return get_trigger_attribute_id(self._trigger_class, self.name)

    def resolve(self, state: BaseState) -> _T:
        trigger_attributes = getattr(state.meta, "trigger_attributes", {})
        if self in trigger_attributes:
            return cast(_T, trigger_attributes[self])

        if state.meta.parent:
            return self.resolve(state.meta.parent)

        if type(None) in self.types:
            return cast(_T, None)

        raise NodeException(
            message=f"Missing trigger attribute '{self.name}' for {self._trigger_class.__name__}",
            code=WorkflowErrorCode.INVALID_INPUTS,
        )

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
