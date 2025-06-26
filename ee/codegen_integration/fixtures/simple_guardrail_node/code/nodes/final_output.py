from typing import Union

from vellum.workflows.nodes.displayable import FinalOutputNode

from .guardrail_node import GuardrailNode


class FinalOutput(FinalOutputNode[Union[float, int]]):
    class Outputs(FinalOutputNode.Outputs):
        value = GuardrailNode.Outputs.score
