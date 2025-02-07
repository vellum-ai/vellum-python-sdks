from typing import Union

from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .templating_node import TemplatingNode


class FinalOutput(FinalOutputNode[BaseState, Union[float, int]]):
    class Outputs(FinalOutputNode.Outputs):
        value = TemplatingNode.Execution.count
