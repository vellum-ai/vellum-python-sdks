from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.vellum_integration import VellumIntegrationTrigger


# Use inheritance pattern with Schema for type safety
class SlackNewMessage(VellumIntegrationTrigger):
    """Slack trigger using inheritance pattern with typed Schema."""

    provider = "COMPOSIO"
    integration_name = "SLACK"
    slug = "slack_new_message"
    trigger_nano_id = "abc123def456"

    class Schema:
        """Define trigger attributes with type hints for IDE support."""

        message: str
        channel: str


class ProcessMessageNode(BaseNode):
    """Process a Slack message from VellumIntegrationTrigger."""

    class Outputs(BaseNode.Outputs):
        processed_message = SlackNewMessage.message
        channel = SlackNewMessage.channel

    def run(self) -> Outputs:
        return self.Outputs()


class VellumIntegrationTriggerWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Example workflow triggered by VellumIntegrationTrigger (Slack)."""

    graph = SlackNewMessage >> ProcessMessageNode

    class Outputs(BaseWorkflow.Outputs):
        result = ProcessMessageNode.Outputs.processed_message
