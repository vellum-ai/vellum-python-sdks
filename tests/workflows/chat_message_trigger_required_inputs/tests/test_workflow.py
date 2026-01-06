"""Tests for ChatMessageTrigger with required inputs attribute execution."""

from uuid import uuid4

from tests.workflows.chat_message_trigger_required_inputs.workflow import (
    ChatTriggerRequiredInputsWorkflow,
    SimpleChatTrigger,
)


def test_chat_trigger_with_required_inputs_resolves_state_correctly():
    """Tests that workflow with chat trigger and required Inputs resolves state correctly when resolver fails."""

    # GIVEN a workflow with a ChatMessageTrigger and an Inputs interface with a required attribute
    workflow = ChatTriggerRequiredInputsWorkflow()

    # AND a trigger instance with a message
    trigger = SimpleChatTrigger(message="Hello, how can I help you?")

    # AND a previous_execution_id that will cause the resolver to fail
    previous_execution_id = str(uuid4())

    # WHEN we execute the workflow with the trigger and previous_execution_id
    events = list(workflow.stream(trigger=trigger, previous_execution_id=previous_execution_id))

    # THEN the workflow should execute successfully (fall back to default state)
    assert len(events) > 0

    # AND the last event should be workflow.execution.fulfilled
    assert events[-1].name == "workflow.execution.fulfilled"
