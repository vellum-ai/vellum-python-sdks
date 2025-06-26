from vellum.workflows.nodes.displayable import FinalOutputNode

from .code_execution_node import CodeExecutionNode


class FinalOutput(FinalOutputNode[str]):
    class Outputs(FinalOutputNode.Outputs):
        value = CodeExecutionNode.Outputs.result
