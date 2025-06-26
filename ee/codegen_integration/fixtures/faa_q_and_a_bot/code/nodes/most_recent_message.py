from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class MostRecentMessage(TemplatingNode[BaseState, str]):
    template = """{{ chat_history[-1][\"text\"] }}"""
    inputs = {
        "chat_history": Inputs.chat_history,
    }
