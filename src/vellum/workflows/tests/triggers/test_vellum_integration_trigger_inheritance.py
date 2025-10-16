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
