from vellum.workflows.nodes.displayable import FinalOutputNode

from .templating_node_3 import TemplatingNode3


class FinalOutput(FinalOutputNode[str]):
    class Outputs(FinalOutputNode.Outputs):
        value = TemplatingNode3.Outputs.result
