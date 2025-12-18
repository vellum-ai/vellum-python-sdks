"""Tests for ChatMessageTrigger."""

from typing import List

from vellum.client.types import (
    ArrayChatMessageContent,
    ChatMessage,
    ImageChatMessageContent,
    StringChatMessageContent,
    VellumImage,
)
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


def test_chat_message_trigger__array_content_message():
    """Tests that ChatMessageTrigger handles array content with multiple types."""

    # GIVEN a ChatMessageTrigger with an array message containing text and image
    array_content = ArrayChatMessageContent(
        value=[
            StringChatMessageContent(value="Look at this image:"),
            ImageChatMessageContent(value=VellumImage(src="https://example.com/image.jpg")),
        ]
    )
    trigger = ChatMessageTrigger(message=array_content)

    # AND a state with chat_history
    state = ChatState()

    # AND empty outputs
    outputs = BaseOutputs()

    # WHEN the lifecycle hook is called
    trigger.__on_workflow_fulfilled__(state, outputs)

    # THEN the user message is appended with array content
    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].text is None
    assert state.chat_history[0].content == array_content


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
