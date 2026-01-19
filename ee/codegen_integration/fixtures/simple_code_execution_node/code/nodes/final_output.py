from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .code_execution_node import CodeExecutionNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = CodeExecutionNode.Outputs.result

    class Display(FinalOutputNode.Display):
        x = 2392.5396121883655
        y = 235.35180055401668
