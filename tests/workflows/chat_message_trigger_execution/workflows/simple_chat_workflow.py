"""Simple workflow with ChatMessageTrigger for testing."""

from typing import List

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
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


class SimpleChatTrigger(ChatMessageTrigger):
    """Chat trigger that appends workflow output as assistant message."""

    class Config(ChatMessageTrigger.Config):
        output = LazyReference("SimpleChatWorkflow.Outputs.response")  # type: ignore[has-type]
        state = ChatState.chat_history


class SimpleChatWorkflow(BaseWorkflow[BaseInputs, ChatState]):
    """Workflow using SimpleChatTrigger with workflow output reference."""

    graph = SimpleChatTrigger >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response
        chat_history = ChatState.chat_history
