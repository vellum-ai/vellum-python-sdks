from vellum.workflows.nodes.displayable.final_output_node.node import FinalOutputNode

from .my_prompt_node import MyPromptNode


class ExitNode(FinalOutputNode):
    class Outputs(FinalOutputNode.Outputs):
        value = MyPromptNode.Outputs.text
