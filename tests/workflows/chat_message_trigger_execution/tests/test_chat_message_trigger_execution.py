"""Tests for ChatMessageTrigger workflow execution."""

from vellum.client.types import ChatMessage
from vellum.workflows.events.workflow import WorkflowExecutionSnapshottedEvent
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import (
    ChatState,
    SimpleChatTrigger,
    SimpleChatWorkflow,
)


def test_chat_message_trigger__workflow_output_reference():
    """Tests that ChatMessageTrigger resolves workflow output references and reflects in outputs."""

    # GIVEN a workflow using SimpleChatTrigger (subclass with workflow output reference)
    workflow = SimpleChatWorkflow()

    # AND a trigger with message
    trigger = SimpleChatTrigger(message="Hello")

    # WHEN we run the workflow with the trigger
    terminal_event = workflow.run(trigger=trigger)

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the response output is correct
    assert terminal_event.outputs["response"] == "Hello from assistant!"

    # AND the chat_history output contains both user and assistant messages
    chat_history = terminal_event.outputs["chat_history"]
    assert len(chat_history) == 2
    assert chat_history[0].role == "USER"
    assert chat_history[0].text == "Hello"
    assert chat_history[1].role == "ASSISTANT"
    assert chat_history[1].text == "Hello from assistant!"

    # AND the final state also has the updated chat history
    final_state = terminal_event.body.final_state
    assert final_state is not None
    assert isinstance(final_state, ChatState)
    assert len(final_state.chat_history) == 2
    assert final_state.chat_history[0].role == "USER"
    assert final_state.chat_history[0].text == "Hello"
    assert final_state.chat_history[1].role == "ASSISTANT"
    assert final_state.chat_history[1].text == "Hello from assistant!"


def test_chat_message_trigger__emits_snapshot_events_for_trigger_state_mutations():
    """Tests that snapshot events are emitted when trigger mutates state in lifecycle hooks."""

    # GIVEN a workflow using SimpleChatTrigger
    workflow = SimpleChatWorkflow()

    # AND a trigger with message
    trigger = SimpleChatTrigger(message="Hello")

    # WHEN we stream the workflow events with all_workflow_event_filter to include snapshot events
    events = list(workflow.stream(trigger=trigger, event_filter=all_workflow_event_filter))

    # THEN we should have snapshot events for the trigger's state mutations
    snapshot_events = [e for e in events if isinstance(e, WorkflowExecutionSnapshottedEvent)]

    # AND there should be at least 2 snapshot events (one for user message, one for assistant message)
    # These are emitted when ChatMessageTrigger appends to chat_history in __on_workflow_initiated__
    # and __on_workflow_fulfilled__
    assert len(snapshot_events) >= 2, f"Expected at least 2 snapshot events, got {len(snapshot_events)}"

    # AND there should be a snapshot event with just the user message (from __on_workflow_initiated__)
    user_message_snapshot = next(
        (
            e
            for e in snapshot_events
            if e.state.chat_history
            == [
                ChatMessage(role="USER", text="Hello", content=None, source=None),
            ]
        ),
        None,
    )
    assert user_message_snapshot is not None, "Expected a snapshot event with just the user message"

    # AND the last snapshot event should contain the full chat history with both messages
    # (from __on_workflow_fulfilled__)
    last_snapshot = snapshot_events[-1]
    assert last_snapshot.state.chat_history == [
        ChatMessage(role="USER", text="Hello", content=None, source=None),
        ChatMessage(role="ASSISTANT", text="Hello from assistant!", content=None, source=None),
    ]

    # AND the snapshot events should appear before the fulfilled event
    event_names = [e.name for e in events]
    last_snapshot_idx = max(i for i, e in enumerate(events) if isinstance(e, WorkflowExecutionSnapshottedEvent))
    fulfilled_idx = next(i for i, name in enumerate(event_names) if name == "workflow.execution.fulfilled")
    assert last_snapshot_idx < fulfilled_idx, "Snapshot events should appear before fulfilled event"
