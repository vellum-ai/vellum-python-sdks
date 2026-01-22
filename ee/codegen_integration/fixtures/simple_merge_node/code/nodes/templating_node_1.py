from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState


class TemplatingNode1(TemplatingNode[BaseState, str]):
    template = """Hello, world!"""
    inputs = {}

    class Display(TemplatingNode.Display):
        x = 1824.7678784335756
        y = -124.21640253267435
