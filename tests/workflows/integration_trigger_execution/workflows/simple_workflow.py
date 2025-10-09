"""Simple workflow with SlackTrigger for testing."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger


class SimpleNode(BaseNode):
    """Simple node that uses trigger outputs."""

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        message = SlackTrigger.Outputs.message.resolve(self.state)
        channel = SlackTrigger.Outputs.channel.resolve(self.state)
        return self.Outputs(result=f"Received '{message}' from channel {channel}")


class SimpleSlackWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Simple workflow with SlackTrigger."""

    graph = SlackTrigger >> SimpleNode

    class Outputs(BaseWorkflow.Outputs):
        result = SimpleNode.Outputs.result
