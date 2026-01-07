"""Tests for ChatMessageTrigger with custom state reference serialization."""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_custom_state.workflows.custom_state_workflow import CustomStateWorkflow


def test_custom_state_workflow_serialization():
    """CustomStateWorkflow serializes correctly with ChatMessageTrigger using custom state reference."""

    # GIVEN a Workflow that uses a ChatMessageTrigger with custom state reference
    # WHEN we serialize it
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
