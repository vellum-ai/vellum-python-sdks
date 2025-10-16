"""Tests for the inheritance-based VellumIntegrationTrigger helpers."""

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
        trigger_nano_id="nano-123",
        exposed_attributes=("channel", "user", "timestamp"),
    )


def test_from_config_creates_subclass() -> None:
    config = _slack_config()
    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    assert issubclass(SlackTrigger, VellumIntegrationTrigger)
    assert SlackTrigger.provider == VellumIntegrationProviderType.COMPOSIO
    assert SlackTrigger.integration_name == "SLACK"
    assert SlackTrigger.slug == "slack_new_message"
    assert SlackTrigger.trigger_nano_id == "nano-123"
    assert SlackTrigger.attributes == {}
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


def test_to_exec_config_round_trip() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    exec_config = SlackTrigger.to_exec_config()

    assert exec_config.type == "COMPOSIO_INTEGRATION_TRIGGER"
    assert exec_config.provider == VellumIntegrationProviderType.COMPOSIO
    assert exec_config.integration_name == "SLACK"
    assert exec_config.slug == "slack_new_message"
    assert exec_config.trigger_nano_id == "nano-123"
    assert exec_config.attributes is None


def test_from_raw_helper_populates_annotations() -> None:
    config = VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="nano-123",
        exposed_attributes=["channel"],
    )

    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    assert SlackTrigger.__name__ == "SlackNewMessageTrigger"
    assert SlackTrigger.channel.name == "channel"
