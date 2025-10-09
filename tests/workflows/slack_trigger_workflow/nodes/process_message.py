from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.triggers.slack import SlackTrigger


class ProcessMessageNode(BaseNode):
    """Process a Slack message."""

    class Outputs(BaseNode.Outputs):
        processed_message: str

    def run(self) -> Outputs:
        # Access and resolve the message from SlackTrigger outputs
        slack_message = SlackTrigger.Outputs.message.resolve(self.state)
        return self.Outputs(processed_message=f"Processed: {slack_message}")
