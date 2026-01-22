from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode
from vellum.workflows.state import BaseState


class TemplatingNode(BaseTemplatingNode[BaseState, str]):
    template = """Hello, world!"""
    inputs = {}

    class Display(BaseTemplatingNode.Display):
        x = 2001.775709833795
        y = 296.65438885041556
