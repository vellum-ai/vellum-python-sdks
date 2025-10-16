"""Configuration helpers for dynamic Vellum integration triggers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import json
import re
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from vellum.workflows.constants import VellumIntegrationProviderType

TriggerCacheKey = Tuple[str, str, str, str]


def _to_pascal_case(value: str) -> str:
    """Convert identifiers like 'SLACK_NEW_MESSAGE' into 'SlackNewMessage'."""

    chunks = re.split(r"[^0-9A-Za-z]+", value)
    return "".join(chunk.capitalize() for chunk in chunks if chunk)


@dataclass(frozen=True)
class VellumIntegrationTriggerConfig:
    """Normalized integration trigger metadata used to synthesize subclasses."""

    provider: VellumIntegrationProviderType
    integration_name: str
    slug: str
    trigger_nano_id: Optional[str] = None
    filter_attributes: Mapping[str, Any] = field(default_factory=dict)
    attribute_names: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        filter_map = self._validate_filter_attributes(self.filter_attributes)
        object.__setattr__(self, "filter_attributes", filter_map)
        object.__setattr__(self, "attribute_names", tuple(self.attribute_names))

    def identity(self) -> TriggerCacheKey:
        """Stable identity tuple used for caching and UUID generation."""

        frozen_attrs = json.dumps(self.filter_attributes or {}, sort_keys=True, separators=(",", ":"))
        return (
            self.provider.value,
            self.integration_name,
            self.slug,
            frozen_attrs,
        )

    def sanitized_class_name(self) -> str:
        """Create a valid Python class name (PascalCase) from integration metadata."""

        integration_part = _to_pascal_case(self.integration_name)
        slug_part = _to_pascal_case(self.slug)
        if self.slug.lower().startswith(self.integration_name.lower()):
            base_name = f"{slug_part}Trigger"
        else:
            base_name = f"{integration_part}{slug_part}Trigger"
        sanitized = re.sub(r"[^0-9A-Za-z_]", "_", base_name)
        if sanitized and sanitized[0].isdigit():
            sanitized = f"Trigger_{sanitized}"
        return sanitized or "VellumIntegrationTrigger"

    def resolved_attribute_names(self) -> Tuple[str, ...]:
        """Attribute names surfaced on the trigger class."""

        if self.attribute_names:
            return self.attribute_names
        return tuple(self.filter_attributes.keys())

    @staticmethod
    def _validate_filter_attributes(filter_attributes: Mapping[str, Any]) -> Dict[str, Any]:
        filter_map = dict(filter_attributes or {})
        if not filter_map:
            return filter_map

        try:
            json.dumps(filter_map, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Trigger attributes must be JSON-serializable (str, int, float, bool, None, list, dict)."
            ) from exc

        return filter_map

    @classmethod
    def from_raw(
        cls,
        *,
        provider: str | VellumIntegrationProviderType,
        integration_name: str,
        slug: str,
        trigger_nano_id: Optional[str] = None,
        filter_attributes: Mapping[str, Any] | None = None,
        attribute_names: Iterable[str] | None = None,
    ) -> VellumIntegrationTriggerConfig:
        """Coerce raw workflow metadata into a normalized config instance.

        `trigger_nano_id` is provided by backend services (e.g., Composio) and is
        not required when authoring workflows locally. Use
        :meth:`with_trigger_nano_id` or
        :meth:`vellum.workflows.triggers.vellum_integration.VellumIntegrationTrigger.bind_backend_metadata`
        to attach it once it becomes available.
        """

        provider_enum = (
            provider if isinstance(provider, VellumIntegrationProviderType) else VellumIntegrationProviderType(provider)
        )
        filter_map = dict(filter_attributes or {})
        attribute_list = tuple(attribute_names or ())
        return cls(
            provider=provider_enum,
            integration_name=integration_name,
            slug=slug,
            trigger_nano_id=trigger_nano_id,
            filter_attributes=filter_map,
            attribute_names=attribute_list,
        )

    def with_trigger_nano_id(self, trigger_nano_id: str) -> VellumIntegrationTriggerConfig:
        """Return a copy of this config with the trigger nano id populated."""

        return replace(self, trigger_nano_id=trigger_nano_id)
