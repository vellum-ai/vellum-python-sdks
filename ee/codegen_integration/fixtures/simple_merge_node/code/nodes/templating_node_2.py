from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState


class TemplatingNode2(TemplatingNode[BaseState, str]):
    template = """Goodbye, world!"""
    inputs = {}

    class Display(TemplatingNode.Display):
        x = 1827.1240707957352
        y = 438.20962675410783
