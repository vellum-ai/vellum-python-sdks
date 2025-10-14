from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.slack import SlackTrigger


class ProcessMessageNode(BaseNode):
    """Process a Slack message."""

    class Outputs(BaseNode.Outputs):
        processed_message = SlackTrigger.message

    def run(self) -> Outputs:
        return self.Outputs()


class SlackTriggerWorkflow(BaseWorkflow[BaseInputs, BaseState]):
    """Example workflow triggered by Slack events."""

    graph = SlackTrigger >> ProcessMessageNode

    class Outputs(BaseWorkflow.Outputs):
        result = ProcessMessageNode.Outputs.processed_message
