from vellum.workflows.nodes.bases import BaseNode

from ..inputs import Inputs
from ..integration_models.slack_input import SlackInput


class TestNode(BaseNode):
    channel_id = Inputs.channel_id

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        request = SlackInput(channel=self.channel_id)
        return self.Outputs(result=request.channel)
