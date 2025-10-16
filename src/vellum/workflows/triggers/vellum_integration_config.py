"""Configuration helpers for dynamic Vellum integration triggers."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Any, Dict, Iterable, Mapping, Tuple

from vellum.workflows.constants import VellumIntegrationProviderType

TriggerIdentity = Tuple[str, str, str, str, str]


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
    trigger_nano_id: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    exposed_attributes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        attribute_map = self._validate_attributes(self.attributes)
        object.__setattr__(self, "attributes", attribute_map)
        object.__setattr__(self, "exposed_attributes", tuple(self.exposed_attributes))

    def identity(self) -> TriggerIdentity:
        """Stable identity tuple used for caching and UUID generation."""

        frozen_attrs = json.dumps(self.attributes or {}, sort_keys=True, separators=(",", ":"))
        return (
            self.provider.value,
            self.integration_name,
            self.slug,
            self.trigger_nano_id,
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

    def attribute_names(self) -> Tuple[str, ...]:
        """Attribute names surfaced on the trigger class."""

        if self.exposed_attributes:
            return self.exposed_attributes
        return tuple(self.attributes.keys())

    @staticmethod
    def _validate_attributes(attributes: Mapping[str, Any]) -> Dict[str, Any]:
        attribute_map = dict(attributes or {})
        if not attribute_map:
            return attribute_map

        try:
            json.dumps(attribute_map, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Trigger attributes must be JSON-serializable (str, int, float, bool, None, list, dict)."
            ) from exc

        return attribute_map

    @classmethod
    def from_raw(
        cls,
        *,
        provider: str | VellumIntegrationProviderType,
        integration_name: str,
        slug: str,
        trigger_nano_id: str,
        attributes: Mapping[str, Any] | None = None,
        exposed_attributes: Iterable[str] | None = None,
    ) -> VellumIntegrationTriggerConfig:
        """Coerce raw workflow metadata into a normalized config instance."""

        provider_enum = (
            provider if isinstance(provider, VellumIntegrationProviderType) else VellumIntegrationProviderType(provider)
        )
        attribute_map = dict(attributes or {})
        attribute_list = tuple(exposed_attributes or ())
        return cls(
            provider=provider_enum,
            integration_name=integration_name,
            slug=slug,
            trigger_nano_id=trigger_nano_id,
            attributes=attribute_map,
            exposed_attributes=attribute_list,
        )
