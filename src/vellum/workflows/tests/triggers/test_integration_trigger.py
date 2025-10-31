"""Tests for IntegrationTrigger."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.integration import IntegrationTrigger


def test_requires_config():
    """Trigger classes must declare Config with required fields."""

    # This should fail - no Config class
    with pytest.raises(TypeError, match="Config"):

        class BadTrigger1(IntegrationTrigger):
            message: str
            # Missing Config!

    # This should fail - incomplete Config
    with pytest.raises(TypeError, match="provider"):

        class BadTrigger2(IntegrationTrigger):
            message: str

            class Config(IntegrationTrigger.Config):
                integration_name = "SLACK"
                slug = "slack_new_message"
                # Missing provider!

    # This should work
    class GoodTrigger(IntegrationTrigger):
        message: str
        user: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    assert hasattr(GoodTrigger, "Config")


def test_top_level_annotations_create_references():
    """Top-level type annotations (webhook event attributes) automatically create TriggerAttributeReference."""

    class SlackTrigger(IntegrationTrigger):
        message: str
        user: str
        timestamp: float

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

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

    class Trigger1(IntegrationTrigger):
        message: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    class Trigger2(IntegrationTrigger):
        message: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    # Different class names = different IDs (like nodes)
    # Type ignore: mypy sees message as str, but it's actually TriggerAttributeReference at class level
    assert Trigger1.message.id != Trigger2.message.id  # type: ignore[attr-defined]


def test_populates_dynamic_attributes():
    """Trigger dynamically populates attributes from event_data keys."""

    class GithubPushTrigger(IntegrationTrigger):
        repository: str
        branch: str
        commits: list

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "GITHUB"
            slug = "github_push_event"

    event_data = {
        "repository": "vellum-ai/workflows",
        "branch": "main",
        "commits": ["abc123", "def456"],
    }

    trigger = GithubPushTrigger(**event_data)

    assert trigger.repository == "vellum-ai/workflows"
    assert trigger.branch == "main"
    assert trigger.commits == ["abc123", "def456"]


def test_to_trigger_attribute_values():
    """to_trigger_attribute_values returns correct attribute mappings."""

    class SlackTrigger(IntegrationTrigger):
        message: str
        channel: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    event_data = {"message": "Hello", "channel": "C123"}
    trigger = SlackTrigger(**event_data)

    attr_values = trigger.to_trigger_attribute_values()

    assert len(attr_values) == 2
    for key in attr_values.keys():
        assert isinstance(key, TriggerAttributeReference)
    assert set(attr_values.values()) == {"Hello", "C123"}


def test_empty_event_data():
    """Trigger handles empty event data gracefully."""

    class SlackTrigger(IntegrationTrigger):
        message: str

        class Config(IntegrationTrigger.Config):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"

    trigger = SlackTrigger()

    attr_values = trigger.to_trigger_attribute_values()
    assert attr_values == {}
