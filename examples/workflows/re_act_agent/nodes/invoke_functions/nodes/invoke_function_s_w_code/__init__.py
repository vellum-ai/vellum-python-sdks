from typing import Any

from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.state import BaseState

from ...inputs import Inputs


class InvokeFunctionSWCode(CodeExecutionNode[BaseState, Any]):
    filepath = "./script.py"
    code_inputs = {
        "fn_call": Inputs.item,
    }
    runtime = "PYTHON_3_11_6"
    packages = []
