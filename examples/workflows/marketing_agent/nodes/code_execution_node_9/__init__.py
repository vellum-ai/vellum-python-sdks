from typing import Any

from vellum.workflows.nodes.displayable import CodeExecutionNode
from vellum.workflows.state import BaseState


class CodeExecutionNode9(CodeExecutionNode[BaseState, Any]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []
