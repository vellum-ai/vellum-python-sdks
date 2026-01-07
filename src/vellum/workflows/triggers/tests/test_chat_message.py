"""Tests for ChatMessageTrigger."""

import pytest
from typing import List

from pydantic import Field

from vellum.client.types import (
    ArrayChatMessageContent,
    ArrayChatMessageContentItem,
    ChatMessage,
    ImageChatMessageContent,
    StringChatMessageContent,
    VellumImage,
)
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger


class ChatState(BaseState):
    chat_history: List[ChatMessage] = Field(default_factory=list)


@pytest.mark.parametrize(
    ["message", "expected_content"],
    [
        pytest.param(
            [StringChatMessageContent(value="Hello, world!")],
            ArrayChatMessageContent(value=[StringChatMessageContent(value="Hello, world!")]),
            id="text_string_content",
        ),
        pytest.param(
            [ImageChatMessageContent(value=VellumImage(src="https://example.com/image.jpg"))],
            ArrayChatMessageContent(
                value=[ImageChatMessageContent(value=VellumImage(src="https://example.com/image.jpg"))]
            ),
            id="multimodal_image",
        ),
        pytest.param(
            [
                StringChatMessageContent(value="Look at this image:"),
                ImageChatMessageContent(value=VellumImage(src="https://example.com/image.jpg")),
            ],
            ArrayChatMessageContent(
                value=[
                    StringChatMessageContent(value="Look at this image:"),
                    ImageChatMessageContent(value=VellumImage(src="https://example.com/image.jpg")),
                ]
            ),
            id="text_and_multimodal_array",
        ),
    ],
)
def test_chat_message_trigger__initiated(
    message: List[ArrayChatMessageContentItem],
    expected_content: ArrayChatMessageContent,
):
    """Tests that ChatMessageTrigger appends user message on workflow initiation."""

    # GIVEN a ChatMessageTrigger with a message
    trigger = ChatMessageTrigger(message=message)

    # AND a state with chat_history
    state = ChatState()

    # WHEN the initiated lifecycle hook is called
    trigger.__on_workflow_initiated__(state)

    # THEN the user message is appended to chat_history
    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].text is None
    assert state.chat_history[0].content == expected_content


def test_chat_message_trigger__state_without_chat_history():
    """Tests that ChatMessageTrigger handles state without chat_history gracefully."""

    # GIVEN a ChatMessageTrigger with a message
    trigger = ChatMessageTrigger(message=[StringChatMessageContent(value="Hello")])

    # AND a state without chat_history attribute
    state = BaseState()

    # WHEN the initiated lifecycle hook is called
    trigger.__on_workflow_initiated__(state)

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


class CustomChatHistoryState(BaseState):
    messages: List[ChatMessage] = Field(default_factory=list)


class CustomStateTrigger(ChatMessageTrigger):
    """Trigger with custom state reference."""

    class Config(ChatMessageTrigger.Config):
        state = CustomChatHistoryState.messages


def test_chat_message_trigger__custom_state_initiated():
    """Tests that ChatMessageTrigger uses custom state reference on initiation."""

    # GIVEN a ChatMessageTrigger with a custom state reference
    trigger = CustomStateTrigger(message="Hello, world!")

    # AND a state with the custom chat history attribute
    state = CustomChatHistoryState()

    # WHEN the initiated lifecycle hook is called
    trigger.__on_workflow_initiated__(state)

    # THEN the user message is appended to the custom chat history attribute
    assert len(state.messages) == 1
    assert state.messages[0].role == "USER"
    assert state.messages[0].text == "Hello, world!"


def test_chat_message_trigger__custom_state_missing_attribute():
    """Tests that ChatMessageTrigger handles missing custom state attribute gracefully."""

    # GIVEN a ChatMessageTrigger with a custom state reference
    trigger = CustomStateTrigger(message="Hello")

    # AND a state without the custom chat history attribute
    state = BaseState()

    # WHEN the initiated lifecycle hook is called
    trigger.__on_workflow_initiated__(state)

    # THEN no error is raised and state is unchanged
    assert not hasattr(state, "messages")


def test_chat_message_trigger__default_state():
    """Tests that ChatMessageTrigger uses default state (None) which falls back to chat_history."""

    # GIVEN a ChatMessageTrigger with default config
    trigger = ChatMessageTrigger(message="Hello")

    # AND a state with chat_history attribute
    state = ChatState()

    # WHEN we resolve the state
    chat_history = trigger._resolve_state(state)

    # THEN the default state config is None
    assert trigger.Config.state is None

    # AND the resolved chat history is the state's chat_history attribute
    assert chat_history is state.chat_history
