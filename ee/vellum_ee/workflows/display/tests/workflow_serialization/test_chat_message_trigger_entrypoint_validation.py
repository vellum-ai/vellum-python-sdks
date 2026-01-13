import pytest
from typing import List

from pydantic import Field

from vellum.client.types import ChatMessage
from vellum.workflows import BaseWorkflow
from vellum.workflows.graph import Graph
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.references import LazyReference
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


class ChatState(BaseState):
    chat_history: List[ChatMessage] = Field(default_factory=list)


class SimpleNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        response: str = "Hello!"


class AnotherNode(BaseNode):
    class Outputs(BaseNode.Outputs):
        result: str = "Another!"


def test_chat_message_trigger_with_entrypoint_raises_error():
    """
    Tests that serializing a workflow with both ChatMessageTrigger and an entrypoint raises an error.
    """

    # GIVEN a workflow with ChatMessageTrigger that also has a separate entrypoint (multiple subgraphs)
    class SimpleChatTrigger(ChatMessageTrigger):
        class Config(ChatMessageTrigger.Config):
            output = LazyReference(lambda: WorkflowWithEntrypoint.Outputs.response)  # type: ignore[has-type]

    class WorkflowWithEntrypoint(BaseWorkflow[BaseInputs, ChatState]):
        graph = {
            SimpleChatTrigger >> SimpleNode,
            Graph.from_node(AnotherNode),
        }

        class Outputs(BaseWorkflow.Outputs):
            response = SimpleNode.Outputs.response

    # WHEN we try to serialize the workflow
    # THEN it should raise a WorkflowValidationError
    with pytest.raises(WorkflowValidationError) as exc_info:
        get_workflow_display(workflow_class=WorkflowWithEntrypoint).serialize()

    # AND the error message should indicate the mutual exclusivity
    assert "ChatMessageTrigger and entrypoint nodes are mutually exclusive" in str(exc_info.value)


def test_chat_message_trigger_without_entrypoint_does_not_raise_mutual_exclusivity_error():
    """
    Tests that serializing a workflow with only ChatMessageTrigger (no entrypoint) does not raise
    the mutual exclusivity error.
    """

    # GIVEN a workflow with only ChatMessageTrigger (no entrypoint)
    class SimpleChatTrigger(ChatMessageTrigger):
        class Config(ChatMessageTrigger.Config):
            output = LazyReference(lambda: ChatOnlyWorkflow.Outputs.response)  # type: ignore[has-type]

    class ChatOnlyWorkflow(BaseWorkflow[BaseInputs, ChatState]):
        graph = SimpleChatTrigger >> SimpleNode

        class Outputs(BaseWorkflow.Outputs):
            response = SimpleNode.Outputs.response

    # WHEN we try to serialize the workflow
    # THEN it should NOT raise a WorkflowValidationError about mutual exclusivity
    # (it may raise other errors due to ChatMessageTrigger attribute serialization limitations)
    try:
        get_workflow_display(workflow_class=ChatOnlyWorkflow).serialize()
    except WorkflowValidationError as e:
        # If we get a WorkflowValidationError, it should NOT be about mutual exclusivity
        assert "ChatMessageTrigger and entrypoint nodes are mutually exclusive" not in str(
            e
        ), f"Should not raise mutual exclusivity error for ChatMessageTrigger-only workflow, got: {e}"
    except ValueError:
        pass
