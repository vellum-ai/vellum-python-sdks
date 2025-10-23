from vellum.workflows import BaseWorkflow
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState

from tests.workflows.map_node_with_terminal_nodes.inputs import Inputs
from tests.workflows.map_node_with_terminal_nodes.nodes.my_map_node import MyMapNode
from tests.workflows.map_node_with_terminal_nodes.nodes.output import Output


class MapNodeWithTerminalNodes(BaseWorkflow[Inputs, BaseState]):
    graph = MyMapNode >> Output

    class Outputs(BaseOutputs):
        final_result = Output.Outputs.value
