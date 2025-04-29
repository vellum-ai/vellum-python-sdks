from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.state import BaseState

from ..allowed_function_names import AllowedFunctionNames
from ..parse_function_name import ParseFunctionName


class IsValidFunctionName(CodeExecutionNode[BaseState, str]):
    filepath = "./script.py"
    code_inputs = {
        "function_name": ParseFunctionName.Outputs.result,
        "allowed_function_names": AllowedFunctionNames.Outputs.result,
    }
    runtime = "PYTHON_3_11_6"
    packages = []
