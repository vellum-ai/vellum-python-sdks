"""Tests for VellumIntegrationTrigger inheritance pattern."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


def test_inheritance_requires_config():
    """Inheritance classes must declare Config with required fields."""

    # This should fail - no Config class
    with pytest.raises(TypeError, match="Config"):

        class BadTrigger1(VellumIntegrationTrigger):
            message: str
            # Missing Config!

    # This should fail - incomplete Config
    with pytest.raises(TypeError, match="provider"):

        class BadTrigger2(VellumIntegrationTrigger):
            message: str

            class Config(VellumIntegrationTrigger.Config):
                integration_name = "SLACK"
                slug = "slack_new_message"
                trigger_nano_id = "test_123"
                # Missing provider!

    # This should work
    class GoodTrigger(VellumIntegrationTrigger):
        message: str
        user: str

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"

    assert hasattr(GoodTrigger, "Config")


def test_top_level_annotations_create_references():
    """Top-level type annotations automatically create TriggerAttributeReference."""

    class SlackTrigger(VellumIntegrationTrigger):
        message: str
        user: str
        timestamp: float

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"

    # Should auto-create references from annotations
    assert isinstance(SlackTrigger.message, TriggerAttributeReference)
    assert isinstance(SlackTrigger.user, TriggerAttributeReference)
    assert isinstance(SlackTrigger.timestamp, TriggerAttributeReference)
    assert SlackTrigger.message.types == (str,)
    assert SlackTrigger.timestamp.types == (float,)

    # Undeclared attributes should raise AttributeError
    with pytest.raises(AttributeError):
        _ = SlackTrigger.undefined_attribute


def test_attribute_ids_include_class_name():
    """Attribute IDs should include class name (like nodes)."""

    class Trigger1(VellumIntegrationTrigger):
        message: str

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"

    class Trigger2(VellumIntegrationTrigger):
        message: str

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"

    # Different class names = different IDs (like nodes)
    assert Trigger1.message.id != Trigger2.message.id


def test_populates_dynamic_attributes():
    """Trigger dynamically populates attributes from event_data keys."""

    class GithubPushTrigger(VellumIntegrationTrigger):
        repository: str
        branch: str
        commits: list

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "GITHUB"
            slug = "github_push_event"
            trigger_nano_id = "test_456"

    event_data = {
        "repository": "vellum-ai/workflows",
        "branch": "main",
        "commits": ["abc123", "def456"],
    }

    trigger = GithubPushTrigger(event_data=event_data)

    assert trigger.repository == "vellum-ai/workflows"
    assert trigger.branch == "main"
    assert trigger.commits == ["abc123", "def456"]


def test_to_trigger_attribute_values():
    """to_trigger_attribute_values returns correct attribute mappings."""

    class SlackTrigger(VellumIntegrationTrigger):
        message: str
        channel: str

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"

    event_data = {"message": "Hello", "channel": "C123"}
    trigger = SlackTrigger(event_data=event_data)

    attr_values = trigger.to_trigger_attribute_values()

    assert len(attr_values) == 2
    for key in attr_values.keys():
        assert isinstance(key, TriggerAttributeReference)
    assert set(attr_values.values()) == {"Hello", "C123"}


def test_to_exec_config():
    """to_exec_config() produces valid ComposioIntegrationTriggerExecConfig."""

    class SlackTrigger(VellumIntegrationTrigger):
        message: str
        user: str

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "abc123def456"

    exec_config = SlackTrigger.to_exec_config()

    assert exec_config.type == "VELLUM_INTEGRATION_TRIGGER"
    assert exec_config.provider == VellumIntegrationProviderType.COMPOSIO
    assert exec_config.integration_name == "SLACK"
    assert exec_config.slug == "slack_new_message"
    assert exec_config.trigger_nano_id == "abc123def456"
    assert exec_config.event_attributes == {"message": str, "user": str}


def test_to_exec_config_base_class_fails():
    """to_exec_config() raises error on base class."""
    with pytest.raises(AttributeError):
        VellumIntegrationTrigger.to_exec_config()


def test_empty_event_data():
    """Trigger handles empty event data gracefully."""

    class SlackTrigger(VellumIntegrationTrigger):
        message: str

        class Config(VellumIntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"

    trigger = SlackTrigger(event_data={})

    attr_values = trigger.to_trigger_attribute_values()
    assert attr_values == {}
