from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """Hello, world!"""
    inputs = {}
