from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.nodes.core.map_node.node import MapNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class NodeToMock(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str

    def run(self) -> Outputs:
        raise NodeException("This node should be mocked")


class SimpleSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = NodeToMock

    class Outputs(BaseWorkflow.Outputs):
        final_value = NodeToMock.Outputs.result


class MapFruitNode(MapNode):
    items = ["apple", "banana", "cherry"]
    subworkflow = SimpleSubworkflow


class NestedNodeMockWorkflow(BaseWorkflow):
    """
    A Workflow that contains a MapNode that contains the actual node we want to mock
    """

    graph = MapFruitNode

    class Outputs(BaseWorkflow.Outputs):
        final_value = MapFruitNode.Outputs.final_value
