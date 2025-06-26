from typing import Union

from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .guardrail_node import GuardrailNode


class FinalOutput(FinalOutputNode[BaseState, Union[float, int]]):
    class Outputs(FinalOutputNode.Outputs):
        value = GuardrailNode.Outputs.score
