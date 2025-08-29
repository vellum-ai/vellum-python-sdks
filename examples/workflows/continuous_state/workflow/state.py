from typing import Any, Optional, Union

from vellum.workflows.state import BaseState


class State(BaseState):
    conversation_history: list[str] = []
    message_count: int = 0
