from vellum.workflows import BaseWorkflow

from tests.workflows.circular_lazy_reference.nodes.first import FirstNode
from tests.workflows.circular_lazy_reference.nodes.loop import LoopNode
from tests.workflows.circular_lazy_reference.nodes.second import SecondNode


class CircularLazyReferenceWorkflow(BaseWorkflow):
    """
    This workflow demonstrates a circular reference between two nodes, FirstNode and SecondNode.

    We resolve this by using a LazyReference to the SecondNode's value.
    """

    graph = FirstNode >> SecondNode >> LoopNode.Ports.loop >> FirstNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = LoopNode.Execution.count
