"""Tests for ChatMessageTrigger with required inputs attribute serialization."""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_required_inputs.workflow import ChatTriggerRequiredInputsWorkflow


def test_chat_trigger_required_inputs_serialization():
    """Tests that ChatMessageTrigger attributes serialize with correct required field values."""

    # GIVEN a Workflow that uses a ChatMessageTrigger with both required and optional attributes
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=ChatTriggerRequiredInputsWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow with triggers
    assert "triggers" in serialized_workflow
    assert len(serialized_workflow["triggers"]) == 1

    # AND the trigger should be a CHAT_MESSAGE type
    trigger = serialized_workflow["triggers"][0]
    assert trigger["type"] == "CHAT_MESSAGE"

    # AND the trigger should have attributes
    assert "attributes" in trigger
    attributes = trigger["attributes"]

    # AND we should have both the required 'message' attribute and optional 'context' attribute
    attribute_required_map = {attr["key"]: attr["required"] for attr in attributes}

    # AND the 'context' attribute should be marked as not required (optional)
    assert "context" in attribute_required_map
    assert attribute_required_map["context"] is False

    # AND the 'message' attribute should be marked as required
    assert "message" in attribute_required_map
    assert attribute_required_map["message"] is True
