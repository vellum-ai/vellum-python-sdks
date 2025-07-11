from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """{{ text }} World!!!!"""
    inputs = {
        "text": Inputs.text,
    }
