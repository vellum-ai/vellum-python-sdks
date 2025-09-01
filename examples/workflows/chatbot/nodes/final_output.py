from vellum.workflows.nodes.displayable import FinalOutputNode

from ..state import State
from .chatbot_node import ChatbotNode


class FinalOutput(FinalOutputNode[State, list]):
    class Outputs(FinalOutputNode.Outputs):
        value = ChatbotNode.Outputs.conversation_history
