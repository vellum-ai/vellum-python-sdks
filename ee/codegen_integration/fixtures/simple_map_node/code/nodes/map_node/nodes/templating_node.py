from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState

from ...code_execution_node import CodeExecutionNode
from ..inputs import Inputs


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """{{ var_1 }}"""
    inputs = {
        "example_var": Inputs.items,
        "var_1": CodeExecutionNode.Outputs.result,
    }
