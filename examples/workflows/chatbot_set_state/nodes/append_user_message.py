from vellum.client.types.chat_message import ChatMessage
from vellum.workflows.nodes.displayable.set_state_node.node import SetStateNode

from ..inputs import Inputs
from ..state import State


class AppendUserMessage(SetStateNode[State]):
    operations = {
        # Append the latest user message to the loaded chat history (if any)
        "chat_history": State.chat_history
        + ChatMessage(role="USER", text=Inputs.user_message),
    }

    class Display(SetStateNode.Display):
        icon = "vellum:icon:database"
        color = "purple"
