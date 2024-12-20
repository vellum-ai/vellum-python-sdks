from vellum.workflows import BaseWorkflow
from vellum.workflows.nodes.core.try_node.node import TryNode
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.state.base import BaseState

base_module = __name__.split(".")[:-1]


@TryNode.wrap()
class SimpleCodeExecutionNode(CodeExecutionNode[BaseState, int]):
    filepath = "./tests/code.py"
    code_inputs = {}


class TrySimpleCodeExecutionWorkflow(BaseWorkflow):
    graph = SimpleCodeExecutionNode

    class Outputs(BaseWorkflow.Outputs):
        result = SimpleCodeExecutionNode.Outputs.result
        log = SimpleCodeExecutionNode.Outputs.log
