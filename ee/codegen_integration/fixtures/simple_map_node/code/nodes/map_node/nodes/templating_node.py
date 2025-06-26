from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode

from ...code_execution_node import CodeExecutionNode
from ..inputs import Inputs


class TemplatingNode(BaseTemplatingNode[str]):
    template = """{{ var_1 }}"""
    inputs = {
        "example_var": Inputs.items,
        "var_1": CodeExecutionNode.Outputs.result,
    }
