"""Workflow with ChatMessageTrigger using custom state reference for testing."""

from typing import List

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class CustomChatState(BaseState):
    messages: List[ChatMessage] = Field(default_factory=list)


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello from assistant!"


class CustomStateTrigger(ChatMessageTrigger):
    """Chat trigger that uses custom state reference for chat history."""

    class Config(ChatMessageTrigger.Config):
        output = LazyReference(lambda: CustomStateWorkflow.Outputs.response)  # type: ignore[has-type]
        state = CustomChatState.messages


class CustomStateWorkflow(BaseWorkflow[BaseInputs, CustomChatState]):
    """Workflow using CustomStateTrigger with custom state reference."""

    graph = CustomStateTrigger >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response
        messages = CustomChatState.messages
