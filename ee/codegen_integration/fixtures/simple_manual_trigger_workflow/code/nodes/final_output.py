from vellum.workflows.nodes.displayable import FinalOutputNode

from .simple_node import SimpleNode


class FinalOutput(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = SimpleNode.Outputs.result
