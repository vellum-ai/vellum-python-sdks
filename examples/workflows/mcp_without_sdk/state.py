from typing import List

from vellum import ChatMessage
from vellum.workflows.state import BaseState


class State(BaseState):
    chat_history: List[ChatMessage] = []
