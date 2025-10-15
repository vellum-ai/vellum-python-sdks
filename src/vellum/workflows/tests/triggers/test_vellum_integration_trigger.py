"""Tests for VellumIntegrationTrigger factory pattern and behavior."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


def test_factory_creates_trigger_class() -> None:
    """Factory method creates a trigger class with correct attributes."""
    SlackNewMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
        attributes={"channel": "C123456"},
    )

    assert issubclass(SlackNewMessage, VellumIntegrationTrigger)
    assert SlackNewMessage.provider == VellumIntegrationProviderType.COMPOSIO
    assert SlackNewMessage.integration_name == "SLACK"
    assert SlackNewMessage.slug == "slack_new_message"
    assert SlackNewMessage.trigger_nano_id == "test_nano_123"
    assert SlackNewMessage.attributes == {"channel": "C123456"}


def test_factory_caches_trigger_classes() -> None:
    """Factory returns the same class instance for identical parameters (ensures deterministic UUIDs)."""
    SlackNewMessage1 = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )
    SlackNewMessage2 = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )

    assert SlackNewMessage1 is SlackNewMessage2


def test_populates_dynamic_attributes() -> None:
    """Trigger dynamically populates attributes from event_data keys."""
    GithubPush = VellumIntegrationTrigger.for_trigger(
        integration_name="GITHUB",
        slug="github_push_event",
        trigger_nano_id="test_nano_456",
    )

    event_data = {
        "repository": "vellum-ai/workflows",
        "branch": "main",
        "commits": ["abc123", "def456"],
    }

    trigger = GithubPush(event_data=event_data)

    assert getattr(trigger, "repository") == "vellum-ai/workflows"
    assert getattr(trigger, "branch") == "main"
    assert getattr(trigger, "commits") == ["abc123", "def456"]


def test_supports_attribute_references() -> None:
    """Metaclass creates TriggerAttributeReference dynamically on attribute access."""
    SlackNewMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )

    # Metaclass __getattribute__ creates references for undefined attributes
    message_ref = SlackNewMessage.message
    channel_ref = SlackNewMessage.channel

    assert isinstance(message_ref, TriggerAttributeReference)
    assert isinstance(channel_ref, TriggerAttributeReference)
    assert message_ref.name == "message"
    assert channel_ref.name == "channel"


def test_to_trigger_attribute_values() -> None:
    """to_trigger_attribute_values returns correct attribute mappings."""
    SlackNewMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )

    event_data = {"message": "Hello", "channel": "C123"}
    trigger = SlackNewMessage(event_data=event_data)

    attr_values = trigger.to_trigger_attribute_values()

    assert len(attr_values) == 2
    for key in attr_values.keys():
        assert isinstance(key, TriggerAttributeReference)
    assert set(attr_values.values()) == {"Hello", "C123"}


def test_trigger_attribute_id_stability() -> None:
    """Trigger attribute IDs must be stable across factory calls."""
    Slack1 = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )
    Slack2 = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )

    # Factory caching ensures same class
    assert Slack1 is Slack2

    # Attribute references must be deterministic across accesses
    msg_ref_1 = Slack1.message
    msg_ref_2 = Slack2.message

    # Same trigger class + same attribute name = same reference
    assert msg_ref_1 == msg_ref_2


def test_to_exec_config() -> None:
    """to_exec_config() produces valid ComposioIntegrationTriggerExecConfig."""
    SlackMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="abc123def456",
        attributes={"channel": "C123456"},
    )

    exec_config = SlackMessage.to_exec_config()

    assert exec_config.type == "COMPOSIO_INTEGRATION_TRIGGER"
    assert exec_config.provider == VellumIntegrationProviderType.COMPOSIO
    assert exec_config.integration_name == "SLACK"
    assert exec_config.slug == "slack_new_message"
    assert exec_config.trigger_nano_id == "abc123def456"
    assert exec_config.attributes == {"channel": "C123456"}


def test_to_exec_config_base_class_fails() -> None:
    """to_exec_config() raises error on base class."""
    with pytest.raises(AttributeError, match="factory-generated trigger classes"):
        VellumIntegrationTrigger.to_exec_config()


def test_empty_event_data() -> None:
    """Trigger handles empty event data gracefully."""
    SlackMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )
    trigger = SlackMessage(event_data={})

    attr_values = trigger.to_trigger_attribute_values()
    assert attr_values == {}


def test_attribute_name_does_not_conflict_with_class_variables() -> None:
    """Event data attributes don't conflict with class variables."""
    SlackMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
    )

    # Event data with key that matches a class variable name
    event_data = {"provider": "some_value", "message": "Hello"}
    trigger = SlackMessage(event_data=event_data)

    # Instance attribute should be set from event_data
    assert trigger.provider == "some_value"  # Instance attr from event_data
    # But class variable should be unchanged
    assert SlackMessage.provider == VellumIntegrationProviderType.COMPOSIO


def test_non_json_serializable_attributes_fail_fast() -> None:
    """Non-JSON-serializable attributes raise ValueError with clear message."""

    # Custom objects are not JSON-serializable
    class CustomObject:
        pass

    with pytest.raises(ValueError, match="must be JSON-serializable"):
        VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            slug="slack_new_message",
            trigger_nano_id="test_nano_123",
            attributes={"custom": CustomObject()},
        )

    # Sets are not JSON-serializable
    with pytest.raises(ValueError, match="must be JSON-serializable"):
        VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            slug="slack_new_message",
            trigger_nano_id="test_nano_123",
            attributes={"tags": {"a", "b", "c"}},
        )


def test_nested_json_serializable_attributes_work() -> None:
    """Nested JSON-serializable attributes work correctly."""
    SlackMessage = VellumIntegrationTrigger.for_trigger(
        integration_name="SLACK",
        slug="slack_new_message",
        trigger_nano_id="test_nano_123",
        attributes={
            "channel": "C123456",
            "filters": {"status": "active", "priority": ["high", "medium"]},
            "count": 42,
            "enabled": True,
        },
    )

    assert SlackMessage.attributes == {
        "channel": "C123456",
        "filters": {"status": "active", "priority": ["high", "medium"]},
        "count": 42,
        "enabled": True,
    }
