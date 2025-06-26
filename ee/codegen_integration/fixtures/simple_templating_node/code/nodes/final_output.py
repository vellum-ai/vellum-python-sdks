from typing import Union

from vellum.workflows.nodes.displayable import FinalOutputNode

from .templating_node import TemplatingNode


class FinalOutput(FinalOutputNode[Union[float, int]]):
    class Outputs(FinalOutputNode.Outputs):
        value = TemplatingNode.Execution.count
