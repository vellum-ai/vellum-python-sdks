from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.triggers.slack import SlackTrigger


class ProcessMessageNode(BaseNode):
    """Process a Slack message."""

    class Outputs(BaseNode.Outputs):
        processed_message = SlackTrigger.message

    def run(self) -> Outputs:
        return self.Outputs()
