"""Tests for trigger subclass compatibility (P1 feedback)."""

import pytest

from vellum.workflows import BaseWorkflow
from vellum.workflows.constants import VellumIntegrationProviderType
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


class BaseSlackTrigger(VellumIntegrationTrigger):
    message: str

    class Config(VellumIntegrationTrigger.Config):
        provider = VellumIntegrationProviderType.COMPOSIO
        integration_name = "SLACK"
        slug = "slack_base"


class SpecificSlackMessageTrigger(BaseSlackTrigger):
    channel: str
    user: str

    class Config(BaseSlackTrigger.Config):
        slug = "slack_new_message"


class TestTriggerSubclassCompatibility:
    """Validates workflows accept trigger subclasses per P1 feedback."""

    def test_workflow_accepts_trigger_subclass(self):
        """Workflow declaring BaseSlackTrigger should accept SpecificSlackMessageTrigger instance."""

        class TestNode(BaseNode):
            class Outputs(BaseNode.Outputs):
                result: str

            def run(self) -> Outputs:
                return self.Outputs(result="success")

        class TestWorkflow(BaseWorkflow):
            graph = BaseSlackTrigger >> TestNode

            class Outputs(BaseWorkflow.Outputs):
                result = TestNode.Outputs.result

        trigger = SpecificSlackMessageTrigger(event_data={"message": "test", "channel": "#general", "user": "@alice"})

        result = TestWorkflow().run(trigger=trigger)
        assert result.name == "workflow.execution.fulfilled"

    def test_workflow_rejects_incompatible_trigger(self):
        """Workflow should still reject triggers that aren't subclasses."""

        class UnrelatedTrigger(VellumIntegrationTrigger):
            data: str

            class Config(VellumIntegrationTrigger.Config):
                provider = VellumIntegrationProviderType.COMPOSIO
                integration_name = "OTHER"
                slug = "unrelated"

        class TestNode(BaseNode):
            class Outputs(BaseNode.Outputs):
                result: str

            def run(self) -> Outputs:
                return self.Outputs(result="success")

        class TestWorkflow(BaseWorkflow):
            graph = BaseSlackTrigger >> TestNode

        trigger = UnrelatedTrigger(event_data={"data": "test"})

        with pytest.raises(WorkflowInitializationException) as exc_info:
            TestWorkflow().run(trigger=trigger)

        assert "not compatible with workflow triggers" in str(exc_info.value)

    def test_entrypoint_routing_with_subclass(self):
        """Multi-trigger workflow should route correctly when given trigger subclass."""

        class TestNode(BaseNode):
            class Outputs(BaseNode.Outputs):
                result: str

            def run(self) -> Outputs:
                return self.Outputs(result="slack_path")

        class TestWorkflow(BaseWorkflow):
            graph = {
                ManualTrigger >> TestNode,
                BaseSlackTrigger >> TestNode,
            }

            class Outputs(BaseWorkflow.Outputs):
                result = TestNode.Outputs.result

        trigger = SpecificSlackMessageTrigger(event_data={"message": "test", "channel": "#test", "user": "@bot"})

        result = TestWorkflow().run(trigger=trigger)
        assert result.name == "workflow.execution.fulfilled"
        assert result.body.outputs.result == "slack_path"
