from vellum.workflows import BaseState, CodeExecutionNode


class RawCode(CodeExecutionNode[BaseState, dict[str, str]]):
    filepath = "./script.py"
    code_inputs = {}
    runtime = "PYTHON_3_11_6"
    packages = []
