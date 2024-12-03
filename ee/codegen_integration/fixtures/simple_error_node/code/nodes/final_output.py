from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .error_node import ErrorNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = ErrorNode.Outputs.error
