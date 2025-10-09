from vellum.workflows.nodes.bases.base import BaseNode


class ProcessMessageNode(BaseNode):
    """Process a Slack message."""

    class Outputs(BaseNode.Outputs):
        processed_message: str

    def run(self) -> Outputs:
        # In a real implementation, we would access SlackTrigger.Outputs.message here
        # For now, just return a static message for testing
        return self.Outputs(processed_message="Processed Slack message")
