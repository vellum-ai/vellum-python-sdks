from vellum.workflows.nodes.displayable import FinalOutputNode

from .api_node import ApiNode


class FinalOutput(FinalOutputNode[str]):
    class Outputs(FinalOutputNode.Outputs):
        value = ApiNode.Outputs.text
