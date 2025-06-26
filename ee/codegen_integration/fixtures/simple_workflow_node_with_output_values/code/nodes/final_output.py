from vellum.workflows.nodes.displayable import FinalOutputNode

from .templating_node import TemplatingNode


class FinalOutput(FinalOutputNode[str]):
    class Outputs(FinalOutputNode.Outputs):
        value = TemplatingNode.Outputs.result
