from typing import Optional, Union

from pydantic import Field

from vellum import ChatMessage
from vellum.workflows.state import BaseState


class State(BaseState):
    message_count: Optional[Union[float, int]] = 0
    chat_history: Optional[list[ChatMessage]] = Field(default_factory=list)
