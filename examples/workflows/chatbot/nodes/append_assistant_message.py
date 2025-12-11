from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.nodes.displayable.set_state_node.node import SetStateNode

from ..state import State
from .agent import Agent


class AppendAssistantMessage(SetStateNode[State]):
    operations = {
        "chat_history": State.chat_history + ChatMessage(role="ASSISTANT", text=Agent.Outputs.text),
    }

    class Display(SetStateNode.Display):
        icon = "vellum:icon:database"
        color = "purple"
