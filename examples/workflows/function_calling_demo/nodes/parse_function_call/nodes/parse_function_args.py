from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json

from .parse_function_call import ParseFunctionCall1


class ParseFunctionArgs(TemplatingNode[BaseState, Json]):
    template = """{{ function_call.arguments }}"""
    inputs = {
        "function_call": ParseFunctionCall1.Outputs.result,
    }
