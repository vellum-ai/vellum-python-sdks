from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .summarize_image_by_url_chat_history import SummarizeImageByURLChatHistory


class FinalOutput(FinalOutputNode[BaseState, str]):
    class Outputs(FinalOutputNode.Outputs):
        value = SummarizeImageByURLChatHistory.Outputs.text
