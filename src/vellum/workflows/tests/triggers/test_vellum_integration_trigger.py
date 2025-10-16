"""Tests for the inheritance-based VellumIntegrationTrigger helpers."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger
from vellum.workflows.triggers.vellum_integration_config import VellumIntegrationTriggerConfig
from vellum.workflows.utils.uuids import uuid4_from_hash


def _slack_config() -> VellumIntegrationTriggerConfig:
    return VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_new_message",
        attribute_names=("channel", "user", "timestamp"),
    )


def test_from_config_creates_subclass() -> None:
    config = _slack_config()
    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    assert issubclass(SlackTrigger, VellumIntegrationTrigger)
    assert SlackTrigger.provider == VellumIntegrationProviderType.COMPOSIO
    assert SlackTrigger.integration_name == "SLACK"
    assert SlackTrigger.slug == "slack_new_message"
    assert SlackTrigger.trigger_nano_id is None
    assert SlackTrigger.filter_attributes == {}
    assert SlackTrigger.__name__ == "SlackNewMessageTrigger"


def test_registry_returns_same_class() -> None:
    config = _slack_config()
    SlackTrigger1 = VellumIntegrationTrigger.from_config(config)
    SlackTrigger2 = VellumIntegrationTrigger.from_config(config)

    assert SlackTrigger1 is SlackTrigger2


def test_attribute_references_available_on_class() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    channel_ref = SlackTrigger.channel
    assert isinstance(channel_ref, TriggerAttributeReference)
    assert channel_ref.name == "channel"


def test_attribute_reference_uuid_stability() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    first = SlackTrigger.channel
    second = SlackTrigger.channel

    assert first is second
    assert first.id == second.id


def test_dynamic_attribute_reference_creation() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    # Not declared in exposed attributes but should still resolve dynamically
    message_ref = SlackTrigger.message
    assert isinstance(message_ref, TriggerAttributeReference)
    assert message_ref.name == "message"


def test_trigger_class_id_is_derived_from_config_identity() -> None:
    config = _slack_config()
    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    expected_id = uuid4_from_hash("|".join(config.identity()))
    assert SlackTrigger.__id__ == expected_id


def test_to_exec_config_requires_trigger_id() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    with pytest.raises(RuntimeError, match="trigger_nano_id has not been resolved"):
        SlackTrigger.to_exec_config()


def test_to_exec_config_round_trip() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())
    SlackTrigger.bind_backend_metadata("nano-123")

    exec_config = SlackTrigger.to_exec_config()

    assert exec_config.type == "COMPOSIO_INTEGRATION_TRIGGER"
    assert exec_config.provider == VellumIntegrationProviderType.COMPOSIO
    assert exec_config.integration_name == "SLACK"
    assert exec_config.slug == "slack_new_message"
    assert exec_config.trigger_nano_id == "nano-123"
    assert exec_config.attributes is None


def test_filter_attributes_round_trip() -> None:
    config = VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="nano-123",
        filter_attributes={"channel_filter": "FILTER_CHANNEL"},
    )

    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    assert SlackTrigger.filter_attributes == {"channel_filter": "FILTER_CHANNEL"}
    assert SlackTrigger.trigger_nano_id == "nano-123"

    exec_config = SlackTrigger.to_exec_config()
    assert exec_config.attributes == {"channel_filter": "FILTER_CHANNEL"}


def test_bind_backend_metadata_updates_config() -> None:
    config = VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_binding_demo",
        attribute_names=("channel",),
    )

    SlackTrigger = VellumIntegrationTrigger.from_config(config)
    assert SlackTrigger.trigger_nano_id is None

    SlackTrigger.bind_backend_metadata("nano-456")

    assert SlackTrigger.trigger_nano_id == "nano-456"
    assert SlackTrigger.__config__ is not None
    assert SlackTrigger.__config__.trigger_nano_id == "nano-456"


def test_from_raw_helper_populates_annotations() -> None:
    config = VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="nano-123",
        attribute_names=["channel"],
    )

    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    assert SlackTrigger.__name__ == "SlackNewMessageTrigger"
    assert SlackTrigger.channel.name == "channel"


def test_non_serializable_filter_attributes_raise_value_error() -> None:
    class CustomObject:
        pass

    with pytest.raises(ValueError, match="Trigger attributes must be JSON-serializable"):
        VellumIntegrationTriggerConfig.from_raw(
            provider="COMPOSIO",
            integration_name="SLACK",
            slug="slack_new_message",
            trigger_nano_id="nano-123",
            filter_attributes={"custom": CustomObject()},
        )
