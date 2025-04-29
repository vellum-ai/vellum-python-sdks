from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .my_prompt import MyPrompt


class ExitNode(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = MyPrompt.Outputs.text
