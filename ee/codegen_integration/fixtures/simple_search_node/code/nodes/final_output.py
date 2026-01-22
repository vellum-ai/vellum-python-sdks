from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .search_node import SearchNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = SearchNode.Outputs.text

    class Display(FinalOutputNode.Display):
        x = 2750
        y = 210
