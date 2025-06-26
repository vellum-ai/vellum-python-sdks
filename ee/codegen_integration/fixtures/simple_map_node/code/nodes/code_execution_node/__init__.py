from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode

from ...inputs import Inputs


class CodeExecutionNode(BaseCodeExecutionNode[str]):
    filepath = "./script.py"
    code_inputs = {
        "arg1": Inputs.test,
    }
    runtime = "PYTHON_3_11_6"
    packages = []
