from typing import Any

from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .parse_function_args import ParseFunctionArgs


class Args(FinalOutputNode[BaseState, Any]):
    class Outputs(FinalOutputNode.Outputs):
        value = ParseFunctionArgs.Outputs.result
