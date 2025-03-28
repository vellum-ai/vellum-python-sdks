from typing import List

from vellum import ChatMessage
from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    chat_history: List[ChatMessage]
