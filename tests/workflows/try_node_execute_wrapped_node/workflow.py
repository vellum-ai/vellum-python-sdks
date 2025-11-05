from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.nodes.core.try_node.node import TryNode


class InnerNode(BaseNode):
    """
    Inner node that will be wrapped by a Try Node adornment.
    """

    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        return self.Outputs(result="inner_node_executed")


@TryNode.wrap()
class WrappedNode(InnerNode):
    """
    Node wrapped with Try Node adornment.
    """

    pass


class TryNodeExecuteWrappedNodeWorkflow(BaseWorkflow):
    """
    Workflow with a Try Node wrapped node to test execute node API.
    """

    graph = WrappedNode

    class Outputs(BaseWorkflow.Outputs):
        final_result = WrappedNode.Outputs.result
        error = WrappedNode.Outputs.error
