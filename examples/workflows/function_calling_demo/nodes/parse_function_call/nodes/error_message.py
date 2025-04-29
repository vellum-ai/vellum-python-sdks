from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .parse_function_name import ParseFunctionName


class ErrorMessage(TemplatingNode[BaseState, str]):
    template = """Invalid function name {{ invalid_function_name }}."""
    inputs = {
        "invalid_function_name": ParseFunctionName.Outputs.result,
    }
