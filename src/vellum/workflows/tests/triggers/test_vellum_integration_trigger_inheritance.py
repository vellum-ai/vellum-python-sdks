"""Tests for VellumIntegrationTrigger inheritance pattern."""

import pytest

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


def test_inheritance_dynamic_attribute_references():
    """Metaclass should create TriggerAttributeReference for inheritance classes."""

    class SlackTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}

    # This should create a dynamic TriggerAttributeReference
    message_ref = SlackTrigger.message

    assert isinstance(message_ref, TriggerAttributeReference)
    assert message_ref.name == "message"


def test_inheritance_requires_event_attributes():
    """Inheritance classes must declare event_attributes."""

    # This should fail - no event_attributes declared
    with pytest.raises(TypeError, match="event_attributes"):

        class BadTrigger(VellumIntegrationTrigger):
            provider = VellumIntegrationProviderType.COMPOSIO
            integration_name = "SLACK"
            slug = "slack_new_message"
            trigger_nano_id = "test_123"
            # Missing event_attributes!

    # This should work
    class GoodTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {
            "message": str,
            "user": str,
        }

    assert GoodTrigger.event_attributes == {"message": str, "user": str}


def test_event_attributes_create_references():
    """Declared event_attributes automatically create TriggerAttributeReference."""

    class SlackTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {
            "message": str,
            "user": str,
        }

    # Should auto-create references from event_attributes
    assert isinstance(SlackTrigger.message, TriggerAttributeReference)
    assert isinstance(SlackTrigger.user, TriggerAttributeReference)
    assert SlackTrigger.message.types == (str,)

    # Undeclared attributes should raise AttributeError
    with pytest.raises(AttributeError):
        _ = SlackTrigger.undefined_attribute


def test_filter_attributes():
    """Filter attributes are optional and used for event filtering."""

    class SlackTrigger(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}
        filter_attributes = {"channel": "C123456"}

    exec_config = SlackTrigger.to_exec_config()
    assert exec_config.filter_attributes == {"channel": "C123456"}

    # filter_attributes is optional
    class SlackTriggerNoFilter(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_456"
        event_attributes = {"message": str}

    exec_config2 = SlackTriggerNoFilter.to_exec_config()
    assert exec_config2.filter_attributes == {}


def test_attribute_ids_include_class_name():
    """Attribute IDs should include class name (like nodes)."""

    class Trigger1(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}

    class Trigger2(VellumIntegrationTrigger):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_new_message"
        trigger_nano_id = "test_123"
        event_attributes = {"message": str}

    # Different class names = different IDs (like nodes)
    assert Trigger1.message.id != Trigger2.message.id
