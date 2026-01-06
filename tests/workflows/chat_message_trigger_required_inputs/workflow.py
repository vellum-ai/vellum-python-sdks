"""Workflow with ChatMessageTrigger that has both required and optional attributes."""

from typing import List, Optional

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class ChatState(BaseState):
    chat_history: List[ChatMessage] = Field(default_factory=list)


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello from assistant!"


class ChatTriggerWithOptionalContext(ChatMessageTrigger):
    """Chat trigger with both required (message) and optional (context) attributes."""

    context: Optional[str]

    class Config(ChatMessageTrigger.Config):
        output = LazyReference(lambda: ChatTriggerRequiredInputsWorkflow.Outputs.response)  # type: ignore[has-type]


class ChatTriggerRequiredInputsWorkflow(BaseWorkflow[BaseInputs, ChatState]):
    """Workflow using ChatTriggerWithOptionalContext with both required and optional attributes."""

    graph = ChatTriggerWithOptionalContext >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response
        chat_history = ChatState.chat_history
