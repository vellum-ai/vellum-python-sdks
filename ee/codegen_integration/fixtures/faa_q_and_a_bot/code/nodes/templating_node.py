from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState

from .prompt_node import PromptNode


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """{{ json.loads(example_var_1)[\"classification\"] }}"""
    inputs = {
        "example_var_1": PromptNode.Outputs.text,
    }

    class Display(BaseTemplatingNode.Display):
        x = 1474
        y = 540.5
