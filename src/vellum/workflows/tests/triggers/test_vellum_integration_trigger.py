"""Tests for VellumIntegrationTrigger factory pattern and behavior."""

from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.references.trigger import TriggerAttributeReference
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


class TestVellumIntegrationTrigger:
    """Tests for VellumIntegrationTrigger factory pattern and dynamic behavior."""

    def test_factory_creates_trigger_class(self) -> None:
        """Factory method creates a trigger class with correct attributes."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        assert issubclass(SlackNewMessage, VellumIntegrationTrigger)
        assert SlackNewMessage.provider == VellumIntegrationProviderType.COMPOSIO
        assert SlackNewMessage.integration_name == "SLACK"
        assert SlackNewMessage.trigger_name == "SLACK_NEW_MESSAGE"

    def test_factory_caches_trigger_classes(self) -> None:
        """Factory returns the same class instance for identical parameters (ensures deterministic UUIDs)."""
        SlackNewMessage1 = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )
        SlackNewMessage2 = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        assert SlackNewMessage1 is SlackNewMessage2

    def test_populates_dynamic_attributes(self) -> None:
        """Trigger dynamically populates attributes from event_data keys."""
        GithubPush = VellumIntegrationTrigger.for_trigger(
            integration_name="GITHUB",
            trigger_name="GITHUB_PUSH",
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

    def test_supports_attribute_references(self) -> None:
        """Metaclass creates TriggerAttributeReference dynamically on attribute access."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        # Metaclass __getattribute__ creates references for undefined attributes
        message_ref = SlackNewMessage.message
        channel_ref = SlackNewMessage.channel

        assert isinstance(message_ref, TriggerAttributeReference)
        assert isinstance(channel_ref, TriggerAttributeReference)
        assert message_ref.name == "message"
        assert channel_ref.name == "channel"

    def test_to_trigger_attribute_values(self) -> None:
        """to_trigger_attribute_values returns correct attribute mappings."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        event_data = {"message": "Hello", "channel": "C123"}
        trigger = SlackNewMessage(event_data=event_data)

        attr_values = trigger.to_trigger_attribute_values()

        assert len(attr_values) == 2
        for key in attr_values.keys():
            assert isinstance(key, TriggerAttributeReference)
        assert set(attr_values.values()) == {"Hello", "C123"}
