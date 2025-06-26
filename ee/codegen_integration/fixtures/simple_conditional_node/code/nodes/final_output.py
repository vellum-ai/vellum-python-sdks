from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = Inputs.foobar
