"""Tests for the inheritance-based VellumIntegrationTrigger helpers."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger
from vellum.workflows.triggers.vellum_integration_config import VellumIntegrationTriggerConfig


def _slack_config() -> VellumIntegrationTriggerConfig:
    return VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="nano-123",
        attributes={"channel": "C123"},
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
    assert SlackTrigger.attributes == {"channel": "C123"}
    assert SlackTrigger.__name__ == "SlackNewMessageTrigger"


def test_registry_returns_same_class() -> None:
    config = _slack_config()
    SlackTrigger1 = VellumIntegrationTrigger.from_config(config)
    SlackTrigger2 = VellumIntegrationTrigger.from_config(config)

    assert SlackTrigger1 is SlackTrigger2


def test_attribute_references_available_on_class() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    channel_ref = SlackTrigger.channel
    user_ref = SlackTrigger.user

    assert isinstance(channel_ref, TriggerAttributeReference)
    assert isinstance(user_ref, TriggerAttributeReference)
    assert channel_ref.name == "channel"
    assert user_ref.name == "user"


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


def test_instance_populates_event_data() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    event_data = {"channel": "C123", "user": "U456", "message": "Hello"}
    trigger = SlackTrigger(event_data=event_data)

    assert trigger.channel == "C123"
    assert trigger.user == "U456"
    assert trigger.message == "Hello"

    attr_values = trigger.to_trigger_attribute_values()
    assert len(attr_values) == 3
    for reference, value in attr_values.items():
        assert isinstance(reference, TriggerAttributeReference)
        assert value == event_data[reference.name]


def test_to_exec_config_round_trip() -> None:
    SlackTrigger = VellumIntegrationTrigger.from_config(_slack_config())

    exec_config = SlackTrigger.to_exec_config()

    assert exec_config.type == "COMPOSIO_INTEGRATION_TRIGGER"
    assert exec_config.provider == VellumIntegrationProviderType.COMPOSIO
    assert exec_config.integration_name == "SLACK"
    assert exec_config.slug == "slack_new_message"
    assert exec_config.trigger_nano_id == "nano-123"
    assert exec_config.attributes == {"channel": "C123"}


def test_from_raw_helper_populates_annotations() -> None:
    config = VellumIntegrationTriggerConfig.from_raw(
        provider="COMPOSIO",
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="nano-123",
        attributes={"channel": "C123"},
        exposed_attributes=["channel"],
    )

    SlackTrigger = VellumIntegrationTrigger.from_config(config)

    assert SlackTrigger.__name__ == "SlackNewMessageTrigger"
    assert SlackTrigger.channel.name == "channel"


def test_non_serializable_attributes_raise_value_error() -> None:
    class CustomObject:
        pass

    with pytest.raises(ValueError, match="Trigger attributes must be JSON-serializable"):
        VellumIntegrationTriggerConfig.from_raw(
            provider="COMPOSIO",
            integration_name="SLACK",
            slug="slack_new_message",
            trigger_nano_id="nano-123",
            attributes={"custom": CustomObject()},
        )
