from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode

from ..inputs import Inputs


class TemplatingNode(BaseTemplatingNode[str]):
    template = """{{ example_var_1 }}"""
    inputs = {
        "example_var_1": Inputs.text,
    }
