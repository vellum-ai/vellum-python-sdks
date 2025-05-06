from vellum.workflows.nodes import BaseNode

from .my_prompt_node import MyPromptNode


class ExitNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        answer = MyPromptNode.Outputs.text
        thinking = "Returning..."
