"""Tests for ChatMessageTrigger."""

from typing import List

from vellum.client.types import ChatMessage, ImageChatMessageContent, VellumImage
from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class ChatState(BaseState):
    chat_history: List[ChatMessage] = []


def test_chat_message_trigger__text_message():
    """Tests that ChatMessageTrigger handles text messages correctly."""

    # GIVEN a ChatMessageTrigger with a text message
    trigger = ChatMessageTrigger(message="Hello, world!")

    # AND a state with chat_history
    state = ChatState()

    # AND empty outputs
    outputs = BaseOutputs()

    # WHEN the lifecycle hook is called
    trigger.__on_workflow_fulfilled__(state, outputs)

    # THEN the user message is appended to chat_history
    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].text == "Hello, world!"
    assert state.chat_history[0].content is None


def test_chat_message_trigger__multimodal_message():
    """Tests that ChatMessageTrigger handles multi-modal messages correctly."""

    # GIVEN a ChatMessageTrigger with an image message
    image_content = ImageChatMessageContent(value=VellumImage(src="https://example.com/image.jpg"))
    trigger = ChatMessageTrigger(message=image_content)

    # AND a state with chat_history
    state = ChatState()

    # AND empty outputs
    outputs = BaseOutputs()

    # WHEN the lifecycle hook is called
    trigger.__on_workflow_fulfilled__(state, outputs)

    # THEN the user message is appended with content
    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].text is None
    assert state.chat_history[0].content == image_content


def test_chat_message_trigger__with_text_output():
    """Tests that ChatMessageTrigger appends assistant response when output is provided."""

    # GIVEN a ChatMessageTrigger with message and text output
    trigger = ChatMessageTrigger(message="Hello", output="Hi there!")

    # AND a state with chat_history
    state = ChatState()

    # AND empty outputs
    outputs = BaseOutputs()

    # WHEN the lifecycle hook is called
    trigger.__on_workflow_fulfilled__(state, outputs)

    # THEN both user and assistant messages are appended
    assert len(state.chat_history) == 2

    # AND the user message is first
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].text == "Hello"

    # AND the assistant message is second
    assert state.chat_history[1].role == "ASSISTANT"
    assert state.chat_history[1].text == "Hi there!"


def test_chat_message_trigger__state_without_chat_history():
    """Tests that ChatMessageTrigger handles state without chat_history gracefully."""

    # GIVEN a ChatMessageTrigger with a message
    trigger = ChatMessageTrigger(message="Hello")

    # AND a state without chat_history attribute
    state = BaseState()

    # AND empty outputs
    outputs = BaseOutputs()

    # WHEN the lifecycle hook is called
    trigger.__on_workflow_fulfilled__(state, outputs)

    # THEN no error is raised and state is unchanged
    assert not hasattr(state, "chat_history")


def test_chat_message_trigger__graph_syntax():
    """Tests that ChatMessageTrigger can be used in graph syntax."""

    # GIVEN a ChatMessageTrigger and a node
    class TestNode(BaseNode):
        pass

    # WHEN we use trigger >> node syntax
    graph = ChatMessageTrigger >> TestNode

    # THEN a graph is created with the trigger edge
    assert graph is not None
    assert len(list(graph.trigger_edges)) == 1
    assert list(graph.trigger_edges)[0].trigger_class == ChatMessageTrigger
    assert list(graph.trigger_edges)[0].to_node == TestNode


def test_chat_message_trigger__workflow_integration():
    """Tests that ChatMessageTrigger integrates with workflow execution."""

    # GIVEN a simple node that returns a response
    class ResponseNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            response: str = "Hello from assistant!"

    # AND a workflow using ChatMessageTrigger
    class ChatWorkflow(BaseWorkflow[BaseInputs, ChatState]):
        graph = ChatMessageTrigger >> ResponseNode

        class Outputs(BaseWorkflow.Outputs):
            response = ResponseNode.Outputs.response

    # WHEN we run the workflow with a trigger
    workflow = ChatWorkflow()
    trigger = ChatMessageTrigger(message="Hello", output="Hello from assistant!")
    terminal_event = workflow.run(trigger=trigger)

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {"response": "Hello from assistant!"}

    # AND the chat history is updated
    final_state = terminal_event.body.final_state
    assert final_state is not None
    assert isinstance(final_state, ChatState)
    assert len(final_state.chat_history) == 2
    assert final_state.chat_history[0].role == "USER"
    assert final_state.chat_history[0].text == "Hello"
    assert final_state.chat_history[1].role == "ASSISTANT"
    assert final_state.chat_history[1].text == "Hello from assistant!"
