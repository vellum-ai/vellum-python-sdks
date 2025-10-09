import re

from vellum.workflows.nodes import BaseNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class ParseSlackUrlNode(BaseNode[BaseState]):
    slack_url = Inputs.slack_url

    class Outputs(BaseNode.Outputs):
        channel_id: str
        message_ts: str

    def run(self) -> Outputs:
        pattern = "/archives/([A-Z0-9]+)/p(\\d+)"
        match = re.search(pattern, self.slack_url)
        if not match:
            raise ValueError(f"Invalid Slack URL format: {self.slack_url}")
        channel_id = match.group(1)
        raw_ts = match.group(2)
        message_ts = f"{raw_ts[:10]}.{raw_ts[10:]}"
        return self.Outputs(channel_id=channel_id, message_ts=message_ts)
