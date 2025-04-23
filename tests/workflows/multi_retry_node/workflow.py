from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.core.retry_node.node import RetryNode
from vellum.workflows.types.core import MergeBehavior


@RetryNode.wrap(max_attempts=2)
class TopNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        shared: str

    def run(self) -> Outputs:
        return self.Outputs(shared="Hello")


@RetryNode.wrap(max_attempts=2)
class BottomNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        shared: str

    def run(self) -> Outputs:
        return self.Outputs(shared="World")


class LastNode(BaseNode):
    top = TopNode.Outputs.shared
    bottom = BottomNode.Outputs.shared

    class Outputs(BaseNode.Outputs):
        result: str

    class Trigger(BaseNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ALL

    def run(self) -> Outputs:
        return self.Outputs(result=f"{self.top} {self.bottom}")


class MultiRetryWorkflow(BaseWorkflow):
    """
    This workflow shows that we can handle multiple retry nodes defined on a shared node.
    """

    graph = {
        TopNode,
        BottomNode,
    } >> LastNode

    class Outputs:
        final_result = LastNode.Outputs.result
