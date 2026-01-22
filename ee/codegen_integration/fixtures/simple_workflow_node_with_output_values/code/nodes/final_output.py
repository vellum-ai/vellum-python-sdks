from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .templating_node import TemplatingNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = TemplatingNode.Outputs.result

    class Display(FinalOutputNode.Display):
        x = 2750
        y = 211.25540166204985
