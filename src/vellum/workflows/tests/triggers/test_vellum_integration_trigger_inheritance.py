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
