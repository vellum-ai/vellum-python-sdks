"""Simple workflow with only IntegrationTrigger for testing."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode

from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger


class ProcessMessageNode(BaseNode):
    """Node that processes Slack message from trigger."""

    # Reference trigger attributes
    message = SlackMessageTrigger.message
    channel = SlackMessageTrigger.channel

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result=f"Received '{self.message}' from channel {self.channel}")


class SimpleSlackWorkflow(BaseWorkflow):
    """Workflow triggered by Slack messages."""

    graph = SlackMessageTrigger >> ProcessMessageNode

    class Outputs(BaseWorkflow.Outputs):
        result = ProcessMessageNode.Outputs.result
