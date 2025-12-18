"""Simple workflow with ChatMessageTrigger for testing."""

from typing import List

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class ChatState(BaseState):
    chat_history: List[ChatMessage] = []


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello from assistant!"


class SimpleChatTrigger(ChatMessageTrigger):
    """Chat trigger that appends ResponseNode output as assistant message."""

    output = ResponseNode.Outputs.response


class SimpleChatWorkflow(BaseWorkflow[BaseInputs, ChatState]):
    """Workflow triggered by chat messages."""

    graph = SimpleChatTrigger >> ResponseNode

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response
