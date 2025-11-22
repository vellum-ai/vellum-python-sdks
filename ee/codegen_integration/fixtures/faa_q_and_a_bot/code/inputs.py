from typing import Optional

from vellum import ChatMessage
from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    chat_history: Optional[list[ChatMessage]] = None
