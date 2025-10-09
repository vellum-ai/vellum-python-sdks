"""Workflow with both ManualTrigger and IntegrationTrigger for testing multiple entry points."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.manual import ManualTrigger
from vellum.workflows.triggers.slack import SlackTrigger


class SlackPathNode(BaseNode):
    """Node for Slack trigger path."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        message = SlackTrigger.Outputs.message.resolve(self.state)
        return self.Outputs(result=f"Slack: {message}")


class ManualPathNode(BaseNode):
    """Node for manual trigger path."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="Manual execution")


class MultiTriggerWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Workflow with both ManualTrigger and SlackTrigger."""

    graph = {
        SlackTrigger >> SlackPathNode,
        ManualTrigger >> ManualPathNode,
    }

    class Outputs(BaseWorkflow.Outputs):
        slack_result = SlackPathNode.Outputs.result
        manual_result = ManualPathNode.Outputs.result
