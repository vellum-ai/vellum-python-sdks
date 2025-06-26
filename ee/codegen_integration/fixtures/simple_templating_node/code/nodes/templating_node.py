from vellum.workflows.nodes.displayable import TemplatingNode as BaseTemplatingNode


class TemplatingNode(BaseTemplatingNode[str]):
    template = """Hello, world!"""
    inputs = {}
