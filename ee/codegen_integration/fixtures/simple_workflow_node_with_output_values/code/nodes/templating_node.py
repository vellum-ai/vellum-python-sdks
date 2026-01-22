from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState
from vellum.workflows.types.core import MergeBehavior

from ..inputs import Inputs


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """{{ example_var_1 }}"""
    inputs = {
        "example_var_1": Inputs.text,
    }

    class Display(BaseTemplatingNode.Display):
        x = 1934.0008032128517
        y = 219.2219534344094

    class Trigger(BaseTemplatingNode.Trigger):
        merge_behavior = MergeBehavior.AWAIT_ANY
