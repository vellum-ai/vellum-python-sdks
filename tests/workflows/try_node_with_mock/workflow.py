from vellum.workflows import BaseWorkflow
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode


@TryNode.wrap()
class WrappedNode(BaseNode):
    """
    A node wrapped with TryNode adornment that should be mocked in tests.
    """

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        raise NodeException("This node should be mocked")


class TryNodeWithMockWorkflow(BaseWorkflow):
    """
    Workflow with a TryNode-wrapped node to test mocking behavior.
    """

    graph = WrappedNode

    class Outputs(BaseWorkflow.Outputs):
        final_result = WrappedNode.Outputs.result
        error = WrappedNode.Outputs.error
