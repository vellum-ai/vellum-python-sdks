from typing import Any

from vellum.workflows.nodes.displayable import FinalOutputNode

from .map_node import MapNode


class FinalOutput(FinalOutputNode[Any]):
    class Outputs(FinalOutputNode.Outputs):
        value = MapNode.Outputs.final_output
