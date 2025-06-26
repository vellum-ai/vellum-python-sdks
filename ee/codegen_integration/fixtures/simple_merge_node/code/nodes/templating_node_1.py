from vellum.workflows.nodes.displayable import TemplatingNode


class TemplatingNode1(TemplatingNode[str]):
    template = """Hello, world!"""
    inputs = {}
