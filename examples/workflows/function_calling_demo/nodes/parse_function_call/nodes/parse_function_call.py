from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import Json


class ParseFunctionCall1(TemplatingNode[BaseState, Json]):
    template = """{{ output[0] }}"""
    inputs = {
        "output": LazyReference("PromptNode.Outputs.results"),
    }
