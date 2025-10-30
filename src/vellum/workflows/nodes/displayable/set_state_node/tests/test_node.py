import pytest
from typing import List

from vellum import ChatMessage
from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.exceptions import NodeException
from vellum.workflows.nodes.displayable.set_state_node import SetStateNode
from vellum.workflows.state.base import BaseState


def test_set_state_node_with_single_value():
    """Test that SetStateNode can set a single state value."""

    # GIVEN a state with a string field
    class TestState(BaseState):
        message: str = ""

    # AND a SetStateNode that sets a message
    class SetMessage(SetStateNode[TestState]):
        operations = {"message": "Hello, World!"}

    # WHEN we run the node
    state = TestState()
    node = SetMessage(state=state)
    outputs = node.run()

    # THEN the result should be the set value
    assert outputs.result == {"message": "Hello, World!"}

    # AND the state should be updated
    assert state.message == "Hello, World!"


def test_set_state_node_with_multiple_values():
    """Test that SetStateNode can set multiple state values at once with expressions."""

    # GIVEN a state with multiple fields
    class TestState(BaseState):
        counter: int = 0
        total_tokens: int = 0
        user_tokens: int = 5
        assistant_tokens: int = 10

    # AND a SetStateNode that sets multiple values with expressions using add
    class UpdateMultipleState(SetStateNode[TestState]):
        operations = {
            "counter": 1,
            "total_tokens": TestState.user_tokens + TestState.assistant_tokens,
        }

    # WHEN we run the node
    state = TestState()
    node = UpdateMultipleState(state=state)
    outputs = node.run()

    # THEN all state values should be updated
    assert state.counter == 1
    assert state.total_tokens == 15

    # AND the result should contain all updates
    assert outputs.result == {"counter": 1, "total_tokens": 15}


def test_set_state_node_with_chat_history_and_concat():
    """Test that SetStateNode can concatenate chat history using concat."""

    # GIVEN a state with chat history
    class TestState(BaseState):
        chat_history: List[ChatMessage] = []

    # AND initial chat history in state
    initial_messages = [ChatMessage(role="ASSISTANT", text="Hi there")]

    # AND a SetStateNode that uses concat() method to add to chat history
    class UpdateChatHistory(SetStateNode[TestState]):
        operations = {"chat_history": TestState.chat_history.concat([ChatMessage(role="USER", text="Hello")])}

    # WHEN we run the node with initial state
    state = TestState(chat_history=initial_messages)

    node = UpdateChatHistory(state=state)
    outputs = node.run()

    # THEN the state should have concatenated chat history
    assert len(state.chat_history) == 2
    assert state.chat_history[0].role == "ASSISTANT"
    assert state.chat_history[1].role == "USER"
    assert state.chat_history[1].text == "Hello"

    # AND the result should contain the updated chat history
    assert outputs.result == {
        "chat_history": [ChatMessage(role="ASSISTANT", text="Hi there"), ChatMessage(role="USER", text="Hello")]
    }


def test_set_state_node_with_empty_dict():
    """Test that SetStateNode handles empty operations gracefully."""

    # GIVEN a state
    class TestState(BaseState):
        counter: int = 0

    # AND a SetStateNode with empty operations
    class EmptySetState(SetStateNode[TestState]):
        operations = {}

    # WHEN we run the node
    state = TestState()
    node = EmptySetState(state=state)
    outputs = node.run()

    # THEN the result should be an empty dict
    assert outputs.result == {}

    # AND state should be unchanged
    assert state.counter == 0


def test_set_state_node_modifies_existing_values():
    """Test that SetStateNode can modify existing state values."""

    # GIVEN a state with existing values
    class TestState(BaseState):
        counter: int = 10
        message: str = "old"

    # AND a SetStateNode that updates existing values
    class UpdateState(SetStateNode[TestState]):
        operations = {"counter": 20, "message": "new"}

    # WHEN we run the node
    state = TestState()
    node = UpdateState(state=state)
    outputs = node.run()

    # THEN state should be updated
    assert state.counter == 20
    assert state.message == "new"

    # AND result should contain the new values with the correct structure
    assert outputs.result == {"counter": 20, "message": "new"}


def test_set_state_not_existing_value():
    """Test that SetStateNode raises an error when trying to set a value that doesn't exist in the state."""

    # GIVEN a state
    class TestState(BaseState):
        counter: int = 0

    # AND a SetStateNode that tries to set a value that doesn't exist in the state
    class SetState(SetStateNode[TestState]):
        operations = {"unknown_value": 10}

    # WHEN we run the node
    state = TestState()
    node = SetState(state=state)

    # THEN it should raise a NodeException
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # AND the error should be INVALID_STATE and the message should mention the non-existent attribute
    assert exc_info.value.code == WorkflowErrorCode.INVALID_STATE
    assert (
        "State does not have attribute 'unknown_value'. Only existing state attributes can be set via SetStateNode."
        == str(exc_info.value)
    )


def test_set_state_node_atomic_order_independent_resolution():
    """Both operations resolve against the original state before any mutation."""

    class TestState(BaseState):
        a: int = 1
        b: int = 0

    class UpdateAB(SetStateNode[TestState]):
        # Both should see original a=1, so both resolve to 2
        operations = {
            "a": TestState.a + 1,
            "b": TestState.a + 1,
        }

    state = TestState()
    node = UpdateAB(state=state)
    outputs = node.run()

    assert state.a == 2
    assert state.b == 2
    assert outputs.result == {"a": 2, "b": 2}


def test_set_state_node_no_partial_update_on_error():
    """If a later operation is invalid, no earlier changes should be applied."""

    class TestState(BaseState):
        a: int = 5

    class PartialFail(SetStateNode[TestState]):
        operations = {
            "a": 42,  # would change a
            "missing": 1,  # invalid attribute triggers NodeException
        }

    state = TestState()
    node = PartialFail(state=state)

    with pytest.raises(NodeException):
        node.run()

    assert state.a == 5
