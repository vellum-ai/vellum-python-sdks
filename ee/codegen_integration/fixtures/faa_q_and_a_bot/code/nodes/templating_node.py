from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode

from .prompt_node import PromptNode


class TemplatingNode(BaseTemplatingNode[str]):
    template = """{{ json.loads(example_var_1)[\"classification\"] }}"""
    inputs = {
        "example_var_1": PromptNode.Outputs.text,
    }
