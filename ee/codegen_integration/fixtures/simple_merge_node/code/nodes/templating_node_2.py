from vellum.workflows.nodes.displayable import TemplatingNode


class TemplatingNode2(TemplatingNode[str]):
    template = """Goodbye, world!"""
    inputs = {}
