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

    # AND the triggers should be serialized correctly with custom state reference
    assert serialized_workflow["triggers"] == [
        {
            "id": "ee5cb788-8e76-4ddb-af9b-37d3b176acde",
            "type": "CHAT_MESSAGE",
            "attributes": [
                {
                    "id": "6b15244a-d2ee-450f-a702-678e67c62b4a",
                    "key": "message",
                    "type": "JSON",
                    "required": True,
                    "default": {
                        "type": "JSON",
                        "value": None,
                    },
                    "extensions": None,
                    "schema": None,
                }
            ],
            "exec_config": {
                "output": {
                    "type": "WORKFLOW_OUTPUT",
                    "output_variable_id": "02ea4c1b-26a0-4dbb-b9f0-2fad755b794f",
                },
                "state": {
                    "state_variable_id": "8b859454-fd27-4e7b-9436-cfb4fca6fdcc",
                },
            },
            "display_data": {
                "label": "Chat Message",
                "position": {
                    "x": 0.0,
                    "y": 0.0,
                },
                "z_index": 0,
                "icon": "vellum:icon:message-dots",
                "color": "blue",
            },
        }
    ]

    # AND the state_variable_id should match the corresponding state variable
    state_variable_id = serialized_workflow["triggers"][0]["exec_config"]["state"]["state_variable_id"]
    state_variable_ids = [sv["id"] for sv in serialized_workflow["state_variables"]]
    assert state_variable_id in state_variable_ids
