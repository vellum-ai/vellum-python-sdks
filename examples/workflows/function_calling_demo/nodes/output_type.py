from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from .prompt_node import PromptNode


class OutputType(TemplatingNode[BaseState, str]):
    template = """{{ output[0].type }}"""
    inputs = {
        "output": PromptNode.Outputs.results,
    }
