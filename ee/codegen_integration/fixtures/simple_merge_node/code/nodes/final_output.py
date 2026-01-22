from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .templating_node_3 import TemplatingNode3


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = TemplatingNode3.Outputs.result

    class Display(FinalOutputNode.Display):
        x = 3434.5298476454295
        y = 174.57146814404433
