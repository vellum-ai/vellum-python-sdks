from vellum.workflows.nodes.displayable import TemplatingNode

from ..inputs import Inputs


class MostRecentMessage(TemplatingNode[str]):
    template = """{{ chat_history[-1][\"text\"] }}"""
    inputs = {
        "chat_history": Inputs.chat_history,
    }
