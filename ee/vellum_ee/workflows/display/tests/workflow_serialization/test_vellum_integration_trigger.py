"""Tests for VellumIntegrationTrigger factory pattern and behavior."""

import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


class Inputs(BaseInputs):
    input: str


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        output = Inputs.input


class TestVellumIntegrationTriggerFactory:
    """Tests for the VellumIntegrationTrigger.for_trigger() factory method."""

    def test_factory_creates_trigger_class(self) -> None:
        """Factory method creates a trigger class with correct attributes."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        assert SlackNewMessage is not None
        assert issubclass(SlackNewMessage, VellumIntegrationTrigger)
        assert SlackNewMessage.provider == VellumIntegrationProviderType.COMPOSIO
        assert SlackNewMessage.integration_name == "SLACK"
        assert SlackNewMessage.trigger_name == "SLACK_NEW_MESSAGE"

    def test_factory_generates_unique_class_name(self) -> None:
        """Factory generates unique class names."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )
        GithubPush = VellumIntegrationTrigger.for_trigger(
            integration_name="GITHUB",
            trigger_name="GITHUB_PUSH",
        )

        assert SlackNewMessage.__name__ == "VellumIntegrationTrigger_SLACK_SLACK_NEW_MESSAGE"
        assert GithubPush.__name__ == "VellumIntegrationTrigger_GITHUB_GITHUB_PUSH"
        assert SlackNewMessage is not GithubPush

    def test_factory_caches_trigger_classes(self) -> None:
        """Factory returns the same class instance for identical parameters."""
        SlackNewMessage1 = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )
        SlackNewMessage2 = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        assert SlackNewMessage1 is SlackNewMessage2

    def test_factory_supports_different_providers(self) -> None:
        """Factory supports different integration providers."""
        SlackComposio = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
            provider="COMPOSIO",
        )

        assert SlackComposio.provider == VellumIntegrationProviderType.COMPOSIO

    def test_factory_validates_provider(self) -> None:
        """Factory validates provider enum values."""
        with pytest.raises(ValueError):
            VellumIntegrationTrigger.for_trigger(
                integration_name="SLACK",
                trigger_name="SLACK_NEW_MESSAGE",
                provider="INVALID_PROVIDER",  # type: ignore[arg-type]
            )

    def test_factory_sets_module_and_qualname(self) -> None:
        """Factory sets proper __module__ and __qualname__ for serialization."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        assert SlackNewMessage.__module__ == VellumIntegrationTrigger.__module__
        assert SlackNewMessage.__qualname__ == "VellumIntegrationTrigger_SLACK_SLACK_NEW_MESSAGE"


class TestVellumIntegrationTriggerBehavior:
    """Tests for VellumIntegrationTrigger instance behavior."""

    def test_trigger_instantiation_with_event_data(self) -> None:
        """Trigger can be instantiated with event data."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        event_data = {
            "message": "Hello world",
            "channel": "C123456",
            "user": "U789012",
        }

        trigger = SlackNewMessage(event_data=event_data)

        assert trigger.message == "Hello world"  # type: ignore[attr-defined]
        assert trigger.channel == "C123456"  # type: ignore[attr-defined]
        assert trigger.user == "U789012"  # type: ignore[attr-defined]

    def test_trigger_populates_dynamic_attributes(self) -> None:
        """Trigger dynamically populates attributes from event_data keys."""
        GithubPush = VellumIntegrationTrigger.for_trigger(
            integration_name="GITHUB",
            trigger_name="GITHUB_PUSH",
        )

        event_data = {
            "repository": "vellum-ai/workflows",
            "branch": "main",
            "commits": ["abc123", "def456"],
            "pusher": "alex",
        }

        trigger = GithubPush(event_data=event_data)

        assert trigger.repository == "vellum-ai/workflows"  # type: ignore[attr-defined]
        assert trigger.branch == "main"  # type: ignore[attr-defined]
        assert trigger.commits == ["abc123", "def456"]  # type: ignore[attr-defined]
        assert trigger.pusher == "alex"  # type: ignore[attr-defined]

    def test_trigger_works_with_graph_operator(self) -> None:
        """Trigger class works with the >> operator in workflow graphs."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        class TestWorkflow(BaseWorkflow[Inputs, BaseState]):
            graph = SlackNewMessage >> SimpleNode

            class Outputs(BaseWorkflow.Outputs):
                output = SimpleNode.Outputs.output

        # Should not raise any errors
        assert TestWorkflow.graph is not None

    def test_trigger_supports_attribute_references(self) -> None:
        """Trigger supports attribute references for use in nodes."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        # Create a trigger instance to populate attributes
        event_data = {"message": "Test", "channel": "C123"}
        SlackNewMessage(event_data=event_data)  # Populate class attributes

        # Verify class-level attribute access creates references
        # (This mimics what happens in node definitions)
        message_ref = SlackNewMessage.message
        channel_ref = SlackNewMessage.channel

        # References should be TriggerAttributeReference objects
        from vellum.workflows.references.trigger import TriggerAttributeReference

        assert isinstance(message_ref, TriggerAttributeReference)
        assert isinstance(channel_ref, TriggerAttributeReference)
        assert message_ref.name == "message"
        assert channel_ref.name == "channel"

    def test_trigger_state_binding(self) -> None:
        """Trigger can bind attributes to workflow state."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        event_data = {
            "message": "Hello",
            "channel": "C123",
        }

        trigger = SlackNewMessage(event_data=event_data)
        state = BaseState()

        # Bind trigger to state
        trigger.bind_to_state(state)

        # Verify attributes are stored in state
        from vellum.workflows.references.trigger import TriggerAttributeReference

        message_ref = SlackNewMessage.message
        channel_ref = SlackNewMessage.channel

        assert isinstance(message_ref, TriggerAttributeReference)
        assert isinstance(channel_ref, TriggerAttributeReference)

        # Resolve references from state
        assert message_ref.resolve(state) == "Hello"
        assert channel_ref.resolve(state) == "C123"


class TestVellumIntegrationTriggerEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_trigger_with_empty_event_data(self) -> None:
        """Trigger handles empty event data gracefully."""
        SlackNewMessage = VellumIntegrationTrigger.for_trigger(
            integration_name="SLACK",
            trigger_name="SLACK_NEW_MESSAGE",
        )

        trigger = SlackNewMessage(event_data={})

        # Should not raise errors, just have no extra attributes
        assert hasattr(trigger, "_event_data")

    def test_trigger_with_nested_event_data(self) -> None:
        """Trigger handles nested event data structures."""
        GithubPush = VellumIntegrationTrigger.for_trigger(
            integration_name="GITHUB",
            trigger_name="GITHUB_PUSH",
        )

        event_data = {
            "repository": {"name": "workflows", "owner": "vellum-ai"},
            "commits": [{"sha": "abc123", "message": "Initial commit"}],
        }

        trigger = GithubPush(event_data=event_data)

        assert trigger.repository == {"name": "workflows", "owner": "vellum-ai"}  # type: ignore[attr-defined]
        assert trigger.commits == [{"sha": "abc123", "message": "Initial commit"}]  # type: ignore[attr-defined]

    def test_different_triggers_different_cache_keys(self) -> None:
        """Different integration/trigger combinations use different cache keys."""
        Slack1 = VellumIntegrationTrigger.for_trigger("SLACK", "NEW_MESSAGE")
        Slack2 = VellumIntegrationTrigger.for_trigger("SLACK", "REACTION_ADDED")
        Github1 = VellumIntegrationTrigger.for_trigger("GITHUB", "PUSH")

        assert Slack1 is not Slack2
        assert Slack1 is not Github1
        assert Slack2 is not Github1

        # But same params return same instance
        Slack1_again = VellumIntegrationTrigger.for_trigger("SLACK", "NEW_MESSAGE")
        assert Slack1 is Slack1_again
