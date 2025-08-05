from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.state.base import BaseState


class SimpleCodeExecutionNode(CodeExecutionNode[BaseState, int]):
    filepath = "does_not_exist.py"
    code_inputs = {}


class SimpleCodeExecutionWithFilepathWorkflow(BaseWorkflow):
    graph = SimpleCodeExecutionNode

    class Outputs(BaseWorkflow.Outputs):
        result = SimpleCodeExecutionNode.Outputs.result
        log = SimpleCodeExecutionNode.Outputs.log
