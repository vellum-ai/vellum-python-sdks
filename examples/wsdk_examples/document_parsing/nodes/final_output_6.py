from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .extract_by_chat_history import ExtractByChatHistory


class FinalOutput6(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = ExtractByChatHistory.Outputs.text
