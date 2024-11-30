import time

from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class TopNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        return self.Outputs(total=1)


class MiddleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        time.sleep(0.01)
        return self.Outputs(total=1)


class BottomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        time.sleep(0.02)
        return self.Outputs(total=1)


class AwaitAttributesNode(BaseNode[BaseState]):
    top = TopNode.Outputs.total
    middle = MiddleNode.Outputs.total

    class Outputs(BaseNode.Outputs):
        total: int

    def run(self) -> Outputs:
        middle = self.middle or 0
        bottom = self.state.meta.node_outputs.get(BottomNode.Outputs.total, 0)
        print(self.top, middle, bottom)
        return self.Outputs(
            total=self.top + middle + bottom,
        )


class BasicAwaitAttributesWorkflow(BaseWorkflow):
    """
    This Workflow is a minimal example of how the AWAIT_ATTRIBUTE merge behavior works.

    It uses three nodes to show that it is neither AWAIT_ANY (total > 1) nor AWAIT_ALL (total < 3).
    """

    graph = {
        TopNode,
        MiddleNode,
        BottomNode,
    } >> AwaitAttributesNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = AwaitAttributesNode.Outputs.total
