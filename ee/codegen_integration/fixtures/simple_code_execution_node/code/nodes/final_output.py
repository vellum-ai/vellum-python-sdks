from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .code_execution_node import CodeExecutionNode


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = CodeExecutionNode.Outputs.result
