import time

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.workflows.base import BaseWorkflow


class StartNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        value: str

    def run(self) -> Outputs:
        time.sleep(0.2)
        return self.Outputs(value="hello world")


class BasicCancellableWorkflow(BaseWorkflow):
    """
    A long running workflow that can be cancelled.
    """

    graph = StartNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = StartNode.Outputs.value
