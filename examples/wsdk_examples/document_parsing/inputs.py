from typing import List, Optional

from vellum import ChatMessage
from vellum.workflows.inputs import BaseInputs


class Inputs(BaseInputs):
    image_url: str
    workflow_input_chat_history: Optional[List[ChatMessage]]
