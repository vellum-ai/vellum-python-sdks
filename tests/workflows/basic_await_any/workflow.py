import time

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class TopNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        return self.Outputs(total=1)


class BottomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        time.sleep(0.01)
        return self.Outputs(total=1)


class AwaitAnyNode(BaseNode[BaseState]):
    top = TopNode.Outputs.total

    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        bottom = self.state.meta.node_outputs.get(BottomNode.Outputs.total, 0)
        return self.Outputs(
            total=self.top + bottom,
        )


class BasicAwaitAnyWorkflow(BaseWorkflow):
    """
    This Workflow is a minimal example of how the AWAIT_ANY merge behavior works.

    It uses two nodes to show that it returns once the first node completes.
    """

    graph = {
        TopNode,
        BottomNode,
    } >> AwaitAnyNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = AwaitAnyNode.Outputs.total
