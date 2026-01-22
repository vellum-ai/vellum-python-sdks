from typing import Any

from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .map_node import MapNode


class FinalOutput(FinalOutputNode[BaseState, Any]):
    class Outputs(FinalOutputNode.Outputs):
        value = MapNode.Outputs.final_output

    class Display(FinalOutputNode.Display):
        x = 864
        y = 58.5
