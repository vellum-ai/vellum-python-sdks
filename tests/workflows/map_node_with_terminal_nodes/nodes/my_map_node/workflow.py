from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import MapNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState

from tests.workflows.map_node_with_terminal_nodes.nodes.map_iteration_node import MapIterationNode
from tests.workflows.map_node_with_terminal_nodes.nodes.my_map_node.nodes.output import Output


class MapSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = MapIterationNode >> Output

    class Outputs(BaseOutputs):
        processed = Output.Outputs.value
