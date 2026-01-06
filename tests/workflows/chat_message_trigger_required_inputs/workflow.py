"""Workflow with ChatMessageTrigger and Inputs interface with required attribute."""

from typing import List

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.references import LazyReference
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class FailingResolver(BaseWorkflowResolver):
    """A resolver that always fails to load state."""

    def load_state(self, previous_execution_id=None):
        return None

    def get_latest_execution_events(self):
        return iter([])

    def get_state_snapshot_history(self):
        return iter([])


class ChatState(BaseState):
    chat_history: List[ChatMessage] = Field(default_factory=list)


class Inputs(BaseInputs):
    required_value: str


class ResponseNode(BaseNode):
    """Node that returns a simple response."""

    class Outputs(BaseNode.Outputs):
        response: str = "Hello from assistant!"


class SimpleChatTrigger(ChatMessageTrigger):
    """Chat trigger that appends workflow output as assistant message."""

    class Config(ChatMessageTrigger.Config):
        output = LazyReference(lambda: ChatTriggerRequiredInputsWorkflow.Outputs.response)  # type: ignore[has-type]


class ChatTriggerRequiredInputsWorkflow(BaseWorkflow):
    """Workflow with ChatMessageTrigger and Inputs interface with required attribute."""

    graph = SimpleChatTrigger >> ResponseNode
    resolvers = [FailingResolver()]

    class Outputs(BaseWorkflow.Outputs):
        response = ResponseNode.Outputs.response
