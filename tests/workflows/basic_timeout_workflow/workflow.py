import time

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(2.0)
        return self.Outputs(value="hello world")


class BasicTimeoutWorkflow(BaseWorkflow):
    """
    A long running workflow that can timeout.
    """

    graph = StartNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = StartNode.Outputs.value
