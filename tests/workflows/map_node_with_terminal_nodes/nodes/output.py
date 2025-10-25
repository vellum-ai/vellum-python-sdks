from vellum.workflows.nodes.displayable.final_output_node import FinalOutputNode

from tests.workflows.map_node_with_terminal_nodes.nodes.my_map_node import MyMapNode


class Output(FinalOutputNode):
    """Terminal node at the top level"""

    class Outputs(FinalOutputNode.Outputs):
        value = MyMapNode.Outputs.processed
