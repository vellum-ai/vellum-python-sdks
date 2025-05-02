from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .parse_function_call import ParseFunctionCall1


class ParseFunctionName(TemplatingNode[BaseState, str]):
    template = """{{ function_call.name }}"""
    inputs = {
        "function_call": ParseFunctionCall1.Outputs.result,
    }
