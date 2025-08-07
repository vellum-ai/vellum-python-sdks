from vellum.workflows.nodes.displayable import FinalOutputNode

from .prompt_node import PromptNode


class FinalOutput(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = PromptNode.Outputs.text
