from typing import Any

from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .function_result_context import FunctionResultContext


class FinalOutput(FinalOutputNode[BaseState, Any]):
    class Outputs(FinalOutputNode.Outputs):
        value = FunctionResultContext.Outputs.result
