from typing import List

from vellum import ChatMessage
from vellum.workflows.state.base import BaseState


class ToolCallingState(BaseState):
    chat_history: List[ChatMessage] = []
    prompt_iterations: int = 0
    current_prompt_output_index: int = 0
    current_function_calls_processed: int = 0
