from typing import List

from vellum import ChatMessage
from vellum.workflows.nodes.displayable import FinalOutputNode
from vellum.workflows.state import BaseState

from .final_accumulation_of_chat_history import FinalAccumulationOfChatHistory


class FullChatHistoryOutput(FinalOutputNode[BaseState, List[ChatMessage]]):
    class Outputs(FinalOutputNode.Outputs):
        value = FinalAccumulationOfChatHistory.Outputs.result
