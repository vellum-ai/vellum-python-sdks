from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .summarize_image_by_chat_history import SummarizeImageByChatHistory


class FinalOutput6(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = SummarizeImageByChatHistory.Outputs.text
