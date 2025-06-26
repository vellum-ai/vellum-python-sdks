from vellum.workflows.nodes.displayable import TemplatingNode

from .templating_node_1 import TemplatingNode1
from .templating_node_2 import TemplatingNode2


class TemplatingNode3(TemplatingNode[str]):
    template = """\
{{ input_a }}
{{ input_b }}\
"""
    inputs = {
        "input_a": TemplatingNode1.Outputs.result,
        "input_b": TemplatingNode2.Outputs.result,
    }
