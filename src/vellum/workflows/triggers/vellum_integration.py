"""Integration trigger base that supports dynamic subclass synthesis via inheritance."""

from __future__ import annotations

import types
from weakref import WeakValueDictionary
from typing import Any, ClassVar, Dict, Optional, Type, cast

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.base import BaseTriggerMeta
from vellum.workflows.triggers.integration import IntegrationTrigger
from vellum.workflows.triggers.vellum_integration_config import TriggerIdentity, VellumIntegrationTriggerConfig
from vellum.workflows.types import ComposioIntegrationTriggerExecConfig
from vellum.workflows.utils.uuids import uuid4_from_hash


class VellumIntegrationTriggerMeta(BaseTriggerMeta):
    """Metaclass that wires trigger configuration into synthesized subclasses."""

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: Dict[str, Any], **kwargs: Any) -> Any:
        config = kwargs.pop("config", None) or namespace.get("__config__")

        if config is not None and not isinstance(config, VellumIntegrationTriggerConfig):
            raise TypeError("config must be a VellumIntegrationTriggerConfig instance")

        if config is not None:
            namespace["provider"] = config.provider
            namespace["integration_name"] = config.integration_name
            namespace["slug"] = config.slug
            namespace["trigger_nano_id"] = config.trigger_nano_id
            namespace["attributes"] = types.MappingProxyType(dict(config.attributes))
            namespace["__trigger_identity__"] = config.identity()
            namespace["__config__"] = config

            annotations = dict(namespace.get("__annotations__", {}))
            for attr_name in config.attribute_names():
                annotations.setdefault(attr_name, Any)
            namespace["__annotations__"] = annotations

            name = config.sanitized_class_name()
            namespace["__qualname__"] = name

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if config is not None:
            cls.__config__ = config

        return cls

    def __getattribute__(cls, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)

        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        if not issubclass(cls, VellumIntegrationTrigger) or cls is VellumIntegrationTrigger:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

        trigger_cls = cast(Type["VellumIntegrationTrigger"], cls)
        trigger_identity = getattr(trigger_cls, "__trigger_identity__", None)
        if trigger_identity is None:
            raise AttributeError(f"type object '{cls.__name__}' has no attribute '{name}'")

        attribute_ids = super().__getattribute__("__trigger_attribute_ids__")
        if name not in attribute_ids:
            identity_str = "|".join((*trigger_identity, name))
            attribute_ids[name] = uuid4_from_hash(identity_str)

        cache = super().__getattribute__("__trigger_attribute_cache__")
        if name in cache:
            return cache[name]

        reference = TriggerAttributeReference(name=name, types=(object,), instance=None, trigger_class=trigger_cls)
        cache[name] = reference
        return reference


class VellumIntegrationTrigger(IntegrationTrigger, metaclass=VellumIntegrationTriggerMeta):
    """Base class for dynamically defined integration triggers.

    Usage:
        >>> config = VellumIntegrationTriggerConfig.from_raw(
        ...     provider="COMPOSIO",
        ...     integration_name="SLACK",
        ...     slug="slack_new_message",
        ...     trigger_nano_id="nano-123",
        ...     exposed_attributes=("channel", "user"),
        ... )
        >>> SlackNewMessageTrigger = VellumIntegrationTrigger.from_config(config)
        >>> SlackNewMessageTrigger.channel  # TriggerAttributeReference

    The resulting subclass behaves like any other trigger class: it can be used in
    workflow graphs, referenced by downstream nodes, serialized to execution configs,
    and instantiated for testing with event payloads.
    """

    provider: ClassVar[VellumIntegrationProviderType]
    integration_name: ClassVar[str]
    slug: ClassVar[str]
    trigger_nano_id: ClassVar[str]
    attributes: ClassVar[Dict[str, Any]]
    __config__: ClassVar[Optional[VellumIntegrationTriggerConfig]]
    __trigger_identity__: ClassVar[TriggerIdentity]

    _registry: ClassVar[WeakValueDictionary[TriggerIdentity, Type[VellumIntegrationTrigger]]] = WeakValueDictionary()

    def __init__(self, event_data: dict):
        """Populate instance attributes from inbound event data."""

        super().__init__(event_data)
        for key, value in event_data.items():
            setattr(self, key, value)

    def to_trigger_attribute_values(self) -> Dict[TriggerAttributeReference[Any], Any]:
        """Return TriggerAttributeReference → value mappings for dynamic attributes."""

        attribute_values: Dict[TriggerAttributeReference[Any], Any] = {}
        for attr_name in self._event_data.keys():
            reference = getattr(type(self), attr_name, None)
            if isinstance(reference, TriggerAttributeReference):
                attribute_values[reference] = getattr(self, attr_name)
        return attribute_values

    @classmethod
    def to_exec_config(cls) -> ComposioIntegrationTriggerExecConfig:
        """Generate the exec config payload used during serialization."""

        if cls is VellumIntegrationTrigger:
            raise AttributeError("to_exec_config() can only be called on configured integration trigger subclasses.")

        return ComposioIntegrationTriggerExecConfig(
            provider=cls.provider,
            integration_name=cls.integration_name,
            slug=cls.slug,
            trigger_nano_id=cls.trigger_nano_id,
            attributes=dict(cls.attributes) if cls.attributes else None,
        )

    @classmethod
    def from_config(cls, config: VellumIntegrationTriggerConfig) -> Type[VellumIntegrationTrigger]:
        """Create or retrieve a trigger subclass from normalized configuration."""

        identity = config.identity()
        existing = cls._registry.get(identity)
        if existing is not None:
            return existing

        def exec_body(namespace: Dict[str, Any]) -> None:
            namespace["__module__"] = cls.__module__
            namespace["__config__"] = config

        trigger_class = types.new_class(
            config.sanitized_class_name(),
            (cls,),
            {},
            exec_body,
        )

        # Ensure BaseTriggerMeta initialization runs with the injected config
        # by explicitly invoking the metaclass. types.new_class already handles this,
        # so trigger_class is ready to use at this point.

        cls._registry[identity] = cast(Type["VellumIntegrationTrigger"], trigger_class)
        return cast(Type["VellumIntegrationTrigger"], trigger_class)
