from vellum.client.types import CodeExecutionPackage
from vellum.workflows.nodes.displayable import CodeExecutionNode as BaseCodeExecutionNode
from vellum.workflows.state import BaseState

from ...inputs import Inputs


class CodeExecutionNode(BaseCodeExecutionNode[BaseState, str]):
    """This is my code execution node"""

    filepath = "./script.py"
    code_inputs = {
        "arg": Inputs.input,
    }
    runtime = "PYTHON_3_11_6"
    packages = [
        CodeExecutionPackage(name="requests", version="2.26.0", repository="test-repo"),
    ]

    class Display(BaseCodeExecutionNode.Display):
        x = 1816.3157894736842
        y = 213.93599376731305
