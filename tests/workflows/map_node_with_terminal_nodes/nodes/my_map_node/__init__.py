from vellum.workflows.nodes import MapNode

from tests.workflows.map_node_with_terminal_nodes.inputs import Inputs
from tests.workflows.map_node_with_terminal_nodes.nodes.my_map_node.workflow import MapSubworkflow


class MyMapNode(MapNode):
    items = Inputs.items
    subworkflow = MapSubworkflow
