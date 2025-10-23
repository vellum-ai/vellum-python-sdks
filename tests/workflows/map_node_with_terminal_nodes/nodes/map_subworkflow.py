from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes import MapNode
from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state import BaseState

from tests.workflows.map_node_with_terminal_nodes.nodes.map_iteration_node import MapIterationNode


class MapSubworkflowOutput(FinalOutputNode):
    """Terminal node for the map subworkflow"""

    class Outputs(FinalOutputNode.Outputs):
        value = MapIterationNode.Outputs.processed


class MapSubworkflow(BaseWorkflow[MapNode.SubworkflowInputs, BaseState]):
    graph = MapIterationNode >> MapSubworkflowOutput

    class Outputs(BaseOutputs):
        processed = MapSubworkflowOutput.Outputs.value
