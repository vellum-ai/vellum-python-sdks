from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .output_path_taken import OutputPathTaken


class FinalOutput(FinalOutputNode[BaseState, str]):
    """Returns the path taken as workflow output."""

    class Outputs(FinalOutputNode.Outputs):
        value = OutputPathTaken.Outputs.result
