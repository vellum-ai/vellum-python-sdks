from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

from ...inputs import Inputs


class CodeExecutionNode(BaseCodeExecutionNode[BaseState, str]):
    filepath = "./script.py"
    code_inputs = {
        "arg1": Inputs.test,
    }
    runtime = "PYTHON_3_11_6"
    packages = []
