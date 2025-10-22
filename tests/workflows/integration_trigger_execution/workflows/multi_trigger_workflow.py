"""Workflow with both ManualTrigger and IntegrationTrigger for testing."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.triggers.manual import ManualTrigger

from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger


class ManualNode(BaseNode):
    """Node that runs when workflow is triggered manually."""

    class Outputs(BaseNode.Outputs):
        manual_result: str

    def run(self) -> Outputs:
        return self.Outputs(manual_result="Manual execution")


class SlackNode(BaseNode):
    """Node that runs when workflow is triggered by Slack."""

    message = SlackMessageTrigger.message

    class Outputs(BaseNode.Outputs):
        slack_result: str

    def run(self) -> Outputs:
        return self.Outputs(slack_result=f"Slack: {self.message}")


class MultiTriggerWorkflow(BaseWorkflow):
    """Workflow that can be triggered manually or by Slack."""

    graph = {
        ManualTrigger >> ManualNode,
        SlackMessageTrigger >> SlackNode,
    }

    class Outputs(BaseWorkflow.Outputs):
        manual_result = ManualNode.Outputs.manual_result
        slack_result = SlackNode.Outputs.slack_result
