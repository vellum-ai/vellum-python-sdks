"""Tests for ChatMessageTrigger with custom state reference."""

from vellum.client.types import ChatMessage
from vellum.workflows.events.workflow import WorkflowExecutionSnapshottedEvent
from vellum.workflows.workflows.event_filters import all_workflow_event_filter
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_custom_state.workflows.custom_state_workflow import (
    CustomChatState,
    CustomStateTrigger,
    CustomStateWorkflow,
)


def test_chat_message_trigger__custom_state_run():
    """Tests that ChatMessageTrigger uses custom state reference for chat history."""

    # GIVEN a workflow using CustomStateTrigger with custom state reference
    workflow = CustomStateWorkflow()

    # AND a trigger with message
    trigger = CustomStateTrigger(message="Hello")

    # WHEN we run the workflow with the trigger
    terminal_event = workflow.run(trigger=trigger)

    # THEN the workflow completes successfully
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the response output is correct
    assert terminal_event.outputs["response"] == "Hello from assistant!"

    # AND the messages output contains both user and assistant messages
    messages = terminal_event.outputs["messages"]
    assert len(messages) == 2
    assert messages[0].role == "USER"
    assert messages[0].text == "Hello"
    assert messages[1].role == "ASSISTANT"
    assert messages[1].text == "Hello from assistant!"

    # AND the final state also has the updated messages
    final_state = terminal_event.body.final_state
    assert final_state is not None
    assert isinstance(final_state, CustomChatState)
    assert len(final_state.messages) == 2
    assert final_state.messages[0].role == "USER"
    assert final_state.messages[0].text == "Hello"
    assert final_state.messages[1].role == "ASSISTANT"
    assert final_state.messages[1].text == "Hello from assistant!"


def test_chat_message_trigger__custom_state_emits_snapshot_events():
    """Tests that snapshot events are emitted when trigger mutates custom state."""

    # GIVEN a workflow using CustomStateTrigger
    workflow = CustomStateWorkflow()

    # AND a trigger with message
    trigger = CustomStateTrigger(message="Hello")

    # WHEN we stream the workflow events with all_workflow_event_filter to include snapshot events
    events = list(workflow.stream(trigger=trigger, event_filter=all_workflow_event_filter))

    # THEN we should have snapshot events for the trigger's state mutations
    snapshot_events = [e for e in events if isinstance(e, WorkflowExecutionSnapshottedEvent)]

    # AND there should be at least 2 snapshot events (one for user message, one for assistant message)
    assert len(snapshot_events) >= 2, f"Expected at least 2 snapshot events, got {len(snapshot_events)}"

    # AND the first snapshot event should contain just the user message
    user_message_snapshot = snapshot_events[0]
    assert user_message_snapshot.state.messages == [
        ChatMessage(role="USER", text="Hello", content=None, source=None),
    ]

    # AND the last snapshot event should contain the full messages with both messages
    last_snapshot = snapshot_events[-1]
    assert last_snapshot.state.messages == [
        ChatMessage(role="USER", text="Hello", content=None, source=None),
        ChatMessage(role="ASSISTANT", text="Hello from assistant!", content=None, source=None),
    ]


def test_chat_message_trigger__custom_state_serialization():
    """Tests that ChatMessageTrigger serializes custom state reference correctly."""

    # GIVEN a workflow using CustomStateTrigger with custom state reference
    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=CustomStateWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    # AND the trigger should have the state reference in exec_config
    triggers = serialized_workflow["triggers"]
    assert len(triggers) == 1
    assert triggers[0]["type"] == "CHAT_MESSAGE"
    exec_config = triggers[0]["exec_config"]
    assert "state" in exec_config
    assert "state_variable_id" in exec_config["state"]

    # AND the output should also be serialized
    assert "output" in exec_config
