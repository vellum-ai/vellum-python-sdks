from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.foobar

    class Display(FinalOutputNode.Display):
        x = 2750
        y = 210
