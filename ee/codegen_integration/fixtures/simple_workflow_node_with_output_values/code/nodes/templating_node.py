from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import MergeBehavior

from ..inputs import Inputs


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """{{ example_var_1 }}"""
    inputs = {
        "example_var_1": Inputs.text,
    }

    class Trigger(BaseTemplatingNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY
