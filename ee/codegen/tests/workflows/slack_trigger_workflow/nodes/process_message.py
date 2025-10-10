from vellum.workflows.nodes.bases.base import BaseNode


class ProcessMessageNode(BaseNode):
    """Process a Slack message."""

    class Outputs(BaseNode.Outputs):
        processed_message: str

    def run(self) -> Outputs:
        # Access trigger attributes like: SlackTrigger.message, SlackTrigger.channel, etc.
        # For this test, just return a static message
        return self.Outputs(processed_message="Processed Slack message")
