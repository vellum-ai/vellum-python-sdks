from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState


class TemplatingNode2(TemplatingNode[BaseState, str]):
    template = """Goodbye, world!"""
    inputs = {}
