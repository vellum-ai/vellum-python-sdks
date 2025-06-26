from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState


class TemplatingNode1(TemplatingNode[BaseState, str]):
    template = """Hello, world!"""
    inputs = {}
