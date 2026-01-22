from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .subworkflow_node import SubworkflowNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = SubworkflowNode.Outputs.final_output

    class Display(FinalOutputNode.Display):
        x = 2750
        y = 210
