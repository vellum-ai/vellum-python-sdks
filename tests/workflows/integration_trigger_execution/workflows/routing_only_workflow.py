"""Workflow with IntegrationTrigger that doesn't reference trigger attributes."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode

from tests.workflows.integration_trigger_execution.nodes.slack_message_trigger import SlackMessageTrigger


class ConstantOutputNode(BaseNode):
    """Node that returns a constant output without referencing trigger attributes."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="Workflow executed successfully")


class RoutingOnlyWorkflow(BaseWorkflow):
    """Workflow with IntegrationTrigger used only for routing, not for data access."""

    graph = SlackMessageTrigger >> ConstantOutputNode

    class Outputs(BaseWorkflow.Outputs):
        result = ConstantOutputNode.Outputs.result
