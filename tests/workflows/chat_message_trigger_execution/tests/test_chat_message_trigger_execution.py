"""Tests for ChatMessageTrigger workflow execution."""

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import (
    ChatState,
    SimpleChatTrigger,
    SimpleChatWorkflow,
)


def test_chat_message_trigger__workflow_integration():
    """Tests that ChatMessageTrigger integrates with workflow execution."""

    # GIVEN a workflow using SimpleChatTrigger (subclass with output reference)
    workflow = SimpleChatWorkflow()

    # AND a trigger with message
    trigger = SimpleChatTrigger(message="Hello")

    # WHEN we run the workflow with the trigger
    terminal_event = workflow.run(trigger=trigger)

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert terminal_event.outputs == {"response": "Hello from assistant!"}

    # AND the chat history is updated with user message and resolved assistant response
    final_state = terminal_event.body.final_state
    assert final_state is not None
    assert isinstance(final_state, ChatState)
    assert len(final_state.chat_history) == 2
    assert final_state.chat_history[0].role == "USER"
    assert final_state.chat_history[0].text == "Hello"
    assert final_state.chat_history[1].role == "ASSISTANT"
    assert final_state.chat_history[1].text == "Hello from assistant!"
