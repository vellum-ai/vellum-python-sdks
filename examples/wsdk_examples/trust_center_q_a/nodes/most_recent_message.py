from vellum.workflows.nodes.displayable import TemplatingNode
from vellum.workflows.state import BaseState

from ..inputs import Inputs


class MostRecentMessage(TemplatingNode[BaseState, str]):
    """Here we extract the user's individual message. In the next node, we'll use it to search for relevant chunks from previously uploaded security policy PDFs in a Vellum Document Index."""

    template = """{{ chat_history[-1][\"text\"] }}"""
    inputs = {
        "chat_history": Inputs.chat_history,
    }
