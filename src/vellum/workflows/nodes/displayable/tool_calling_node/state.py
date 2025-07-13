from typing import List

from vellum import ChatMessage
from vellum.workflows.state.base import BaseState


class ToolCallingState(BaseState):
    chat_history: List[ChatMessage] = []
    prompt_iterations: int = 0
