"""Tests for VellumIntegrationTrigger inheritance pattern and behavior."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


def test_inheritance_creates_trigger_class() -> None:
    """Inheritance pattern creates a trigger class with correct attributes."""

    class SlackNewMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"
        attributes = {"channel": "C123456"}

        class Schema:
            message: str
            channel: str

    assert issubclass(SlackNewMessage, VellumIntegrationTrigger)
    assert SlackNewMessage.provider == VellumIntegrationProviderType.COMPOSIO
    assert SlackNewMessage.integration_name == "SLACK"
    assert SlackNewMessage.slug == "slack_new_message"
    assert SlackNewMessage.trigger_nano_id == "test_nano_123"
    assert SlackNewMessage.attributes == {"channel": "C123456"}


def test_populates_dynamic_attributes() -> None:
    """Trigger dynamically populates attributes from event_data keys."""

    class GithubPush(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "GITHUB"
        slug = "github_push_event"
        trigger_nano_id = "test_nano_456"

        class Schema:
            repository: str
            branch: str
            commits: list

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
    """Schema pattern creates TriggerAttributeReference for each attribute."""

    class SlackNewMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"

        class Schema:
            message: str
            channel: str

    # Schema processing creates references for defined attributes
    message_ref = SlackNewMessage.message
    channel_ref = SlackNewMessage.channel

    assert isinstance(message_ref, TriggerAttributeReference)
    assert isinstance(channel_ref, TriggerAttributeReference)
    assert message_ref.name == "message"
    assert channel_ref.name == "channel"


def test_to_trigger_attribute_values() -> None:
    """to_trigger_attribute_values returns correct attribute mappings."""

    class SlackNewMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"

        class Schema:
            message: str
            channel: str

    event_data = {"message": "Hello", "channel": "C123"}
    trigger = SlackNewMessage(event_data=event_data)

    attr_values = trigger.to_trigger_attribute_values()

    assert len(attr_values) == 2
    for key in attr_values.keys():
        assert isinstance(key, TriggerAttributeReference)
    assert set(attr_values.values()) == {"Hello", "C123"}


def test_trigger_attribute_id_stability() -> None:
    """Trigger attribute IDs must be stable across class definitions with same configuration."""

    class Slack1(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"

        class Schema:
            message: str

    class Slack2(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"

        class Schema:
            message: str

    # Same semantic identity (provider|integration|slug) = same trigger ID
    assert Slack1.get_trigger_id() == Slack2.get_trigger_id()

    # Attribute references from same semantic trigger should have matching IDs
    assert Slack1.__trigger_attribute_ids__["message"] == Slack2.__trigger_attribute_ids__["message"]


def test_to_exec_config() -> None:
    """to_exec_config() produces valid ComposioIntegrationTriggerExecConfig."""

    class SlackMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "abc123def456"
        attributes = {"channel": "C123456"}

        class Schema:
            message: str
            channel: str

    exec_config = SlackMessage.to_exec_config()

    assert exec_config.type == "COMPOSIO_INTEGRATION_TRIGGER"
    assert exec_config.provider == VellumIntegrationProviderType.COMPOSIO
    assert exec_config.integration_name == "SLACK"
    assert exec_config.slug == "slack_new_message"
    assert exec_config.trigger_nano_id == "abc123def456"
    assert exec_config.attributes == {"channel": "C123456"}


def test_to_exec_config_base_class_fails() -> None:
    """to_exec_config() raises error on base class."""
    with pytest.raises(AttributeError, match="requires a configured trigger class"):
        VellumIntegrationTrigger.to_exec_config()


def test_empty_event_data() -> None:
    """Trigger handles empty event data gracefully."""

    class SlackMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"

        class Schema:
            message: str
            channel: str

    trigger = SlackMessage(event_data={})

    attr_values = trigger.to_trigger_attribute_values()
    assert attr_values == {}


def test_instance_attributes_do_not_conflict_with_class_variables() -> None:
    """Event data can populate instance attributes even if they match class variable names."""

    class SlackMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_nano_123"

        class Schema:
            message: str
            channel: str

    # Event data with key that matches a class variable name
    # Note: "provider" is reserved and won't be in Schema, but can still be in event_data
    event_data = {"provider": "some_value", "message": "Hello", "channel": "C123"}
    trigger = SlackMessage(event_data=event_data)

    # Instance attribute should be set from event_data
    assert trigger.provider == "some_value"  # Instance attr from event_data
    # But class variable should be unchanged
    assert SlackMessage.provider == VellumIntegrationProviderType.COMPOSIO


def test_reserved_names_cannot_be_schema_attributes() -> None:
    """Reserved class variable names cannot be used as Schema attributes."""

    class TestTrigger(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "TEST"
        slug = "test_trigger"
        trigger_nano_id = "test_123"

        class Schema:
            provider: str  # Reserved name - will be skipped
            integration_name: str  # Reserved name - will be skipped
            slug: str  # Reserved name - will be skipped
            message: str  # Valid attribute

    # Only non-reserved attributes should be created as TriggerAttributeReference
    assert isinstance(TestTrigger.message, TriggerAttributeReference)

    # Reserved names should remain as class variables, not TriggerAttributeReference
    assert TestTrigger.provider == VellumIntegrationProviderType.COMPOSIO
    assert TestTrigger.integration_name == "TEST"
    assert TestTrigger.slug == "test_trigger"


def test_get_trigger_id_generates_deterministic_id() -> None:
    """get_trigger_id() returns deterministic UUID based on semantic identity."""

    class SlackMessage(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "abc123"

        class Schema:
            message: str

    trigger_id = SlackMessage.get_trigger_id()
    assert trigger_id == SlackMessage.__id__

    # Same semantic identity = same ID
    class SlackMessageDuplicate(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "different_nano_id"  # nano_id doesn't affect trigger ID

        class Schema:
            message: str
            extra_field: str  # Additional fields don't affect trigger ID

    assert SlackMessage.get_trigger_id() == SlackMessageDuplicate.get_trigger_id()


def test_schema_with_multiple_attributes() -> None:
    """Schema with multiple attributes creates all references correctly."""

    class ComplexTrigger(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "complex_event"
        trigger_nano_id = "test_123"

        class Schema:
            field1: str
            field2: int
            field3: bool
            field4: list

    # All schema attributes should be created as TriggerAttributeReference
    assert isinstance(ComplexTrigger.field1, TriggerAttributeReference)
    assert isinstance(ComplexTrigger.field2, TriggerAttributeReference)
    assert isinstance(ComplexTrigger.field3, TriggerAttributeReference)
    assert isinstance(ComplexTrigger.field4, TriggerAttributeReference)

    # All should have correct names
    assert ComplexTrigger.field1.name == "field1"
    assert ComplexTrigger.field2.name == "field2"
    assert ComplexTrigger.field3.name == "field3"
    assert ComplexTrigger.field4.name == "field4"


def test_attributes_can_be_set_on_subclass() -> None:
    """Attributes class variable can be set for filtering events."""

    class FilteredTrigger(VellumIntegrationTrigger):
        provider = "COMPOSIO"
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        attributes = {
            "channel": "C123456",
            "filters": {"status": "active", "priority": ["high", "medium"]},
            "count": 42,
            "enabled": True,
        }

        class Schema:
            message: str

    assert FilteredTrigger.attributes == {
        "channel": "C123456",
        "filters": {"status": "active", "priority": ["high", "medium"]},
        "count": 42,
        "enabled": True,
    }
