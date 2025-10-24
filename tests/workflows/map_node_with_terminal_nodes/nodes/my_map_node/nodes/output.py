from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode

from tests.workflows.map_node_with_terminal_nodes.nodes.map_iteration_node import MapIterationNode


class Output(FinalOutputNode):
    """Terminal node for the map subworkflow"""

    class Outputs(FinalOutputNode.Outputs):
        value = MapIterationNode.Outputs.processed
