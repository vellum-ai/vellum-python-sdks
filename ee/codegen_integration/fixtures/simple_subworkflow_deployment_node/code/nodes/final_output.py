from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.test

    class Display(FinalOutputNode.Display):
        x = 2750
        y = 211.25540166204985
