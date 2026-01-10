"""Tests for ChatMessageTrigger."""

import pytest
from typing import List, Optional

from pydantic import Field

from vellum.client.types import (
    ArrayChatMessageContent,
    ArrayChatMessageContentItem,
    ChatMessage,
    ImageChatMessageContent,
    StringChatMessageContent,
    StringVellumValue,
    VellumImage,
)
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.triggers.chat_message import ChatMessageTrigger
from vellum.workflows.workflows.base import BaseWorkflow


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


def test_chat_message_trigger__converts_vellum_value_objects():
    """Tests that ChatMessageTrigger converts VellumValue objects to ChatMessageContent."""

    # GIVEN a message as VellumValue objects (as received from codegen/API)
    vellum_value_message = [
        StringVellumValue(type="STRING", value="Hello, world!"),
    ]

    # WHEN a ChatMessageTrigger is created with VellumValue objects
    trigger = ChatMessageTrigger(message=vellum_value_message)

    # THEN the message is converted to ChatMessageContent
    assert len(trigger.message) == 1
    assert isinstance(trigger.message[0], StringChatMessageContent)
    assert trigger.message[0].value == "Hello, world!"

    # AND the trigger works correctly with state
    state = ChatState()
    trigger.__on_workflow_initiated__(state)

    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].content == ArrayChatMessageContent(
        value=[StringChatMessageContent(value="Hello, world!")]
    )


def test_chat_message_trigger__converts_dict_format():
    """Tests that ChatMessageTrigger converts dict format to ChatMessageContent."""

    # GIVEN a message as dict objects (alternative API format)
    dict_message = [
        {"type": "STRING", "value": "Hello from dict!"},
    ]

    # WHEN a ChatMessageTrigger is created with dict objects
    trigger = ChatMessageTrigger(message=dict_message)

    # THEN the message is converted to ChatMessageContent
    assert len(trigger.message) == 1
    assert isinstance(trigger.message[0], StringChatMessageContent)
    assert trigger.message[0].value == "Hello from dict!"


def test_chat_message_trigger__converts_string_message():
    """Tests that ChatMessageTrigger converts string messages to ChatMessageContent list."""

    # GIVEN a message as a string
    string_message = "Hello, world!"

    # WHEN a ChatMessageTrigger is created with a string message
    trigger = ChatMessageTrigger(message=string_message)

    # THEN the message is converted to a list with a single StringChatMessageContent
    assert len(trigger.message) == 1
    assert isinstance(trigger.message[0], StringChatMessageContent)
    assert trigger.message[0].value == "Hello, world!"

    # AND the trigger works correctly with state
    state = ChatState()
    trigger.__on_workflow_initiated__(state)

    assert len(state.chat_history) == 1
    assert state.chat_history[0].role == "USER"
    assert state.chat_history[0].content == ArrayChatMessageContent(
        value=[StringChatMessageContent(value="Hello, world!")]
    )


def test_chat_message_trigger__raw_string_array__workflow_stream():
    """Tests that workflow.stream() works with raw string array after deserialize_trigger."""

    # GIVEN a workflow with ChatMessageTrigger
    class TestNode(BaseNode):
        class Outputs(BaseOutputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result="success")

    class TestWorkflow(BaseWorkflow):
        graph = ChatMessageTrigger >> TestNode

    # AND a raw string array input (not wrapped in VellumValue format)
    raw_string_array_input = {"message": ["Hello", "World"]}

    # WHEN we deserialize the trigger with raw string array
    trigger = TestWorkflow.deserialize_trigger(
        trigger_id=ChatMessageTrigger.__id__,
        inputs=raw_string_array_input,
    )

    # THEN the trigger is properly deserialized
    assert isinstance(trigger, ChatMessageTrigger)
    assert len(trigger.message) == 2
    assert isinstance(trigger.message[0], StringChatMessageContent)
    assert trigger.message[0].value == "Hello"
    assert isinstance(trigger.message[1], StringChatMessageContent)
    assert trigger.message[1].value == "World"

    # AND the workflow can be streamed successfully
    workflow = TestWorkflow()
    events = list(workflow.stream(trigger=trigger))

    # THEN the workflow completes successfully
    assert len(events) > 0


def test_chat_message_trigger__chat_history_defaulted_to_none():
    """Tests that workflow runs successfully when chat_history is defaulted to None."""

    # GIVEN a state with chat_history defaulted to None
    class NullableChatHistoryState(BaseState):
        chat_history: Optional[List[ChatMessage]] = None

    # AND a simple node
    class TestNode(BaseNode):
        class Outputs(BaseOutputs):
            result: str

        def run(self) -> Outputs:
            return self.Outputs(result="success")

    # AND a workflow with ChatMessageTrigger and the nullable chat_history state
    class TestWorkflow(BaseWorkflow[BaseInputs, NullableChatHistoryState]):
        graph = ChatMessageTrigger >> TestNode

    # WHEN we run the workflow with a trigger
    trigger = ChatMessageTrigger(message="Hello")
    workflow = TestWorkflow()
    terminal_event = workflow.run(trigger=trigger)

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the final state has a contentful chat_history
    final_state = terminal_event.final_state
    assert final_state is not None
    assert final_state.chat_history is not None
    assert len(final_state.chat_history) == 1
    assert final_state.chat_history[0].role == "USER"
    assert final_state.chat_history[0].content == ArrayChatMessageContent(
        value=[StringChatMessageContent(value="Hello")]
    )
