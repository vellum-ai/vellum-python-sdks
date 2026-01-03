"""Tests for ChatMessageTrigger serialization."""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import SimpleChatWorkflow


def test_simple_chat_workflow_serialization():
    """SimpleChatWorkflow from tests/workflows serializes correctly with ChatMessageTrigger."""

    # GIVEN a Workflow that uses a ChatMessageTrigger
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=SimpleChatWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    # AND the triggers should be serialized correctly
    assert serialized_workflow["triggers"] == [
        {
            "id": "9e14c49b-c6d9-4fe5-9ff2-835fd695fe5f",
            "type": "CHAT_MESSAGE",
            "attributes": [
                {
                    "id": "5edbfd78-b634-4305-b2ad-d9feecbd5e5f",
                    "key": "message",
                    "type": "STRING",
                    "required": True,
                    "default": {
                        "type": "STRING",
                        "value": "Hello",
                    },
                    "extensions": None,
                    "schema": None,
                }
            ],
            "exec_config": {
                "output": {
                    "type": "NODE_OUTPUT",
                    "node_id": "6c43f557-304c-4f08-a8fd-13d1fb02d96a",
                    "node_output_id": "14f1265b-d5fb-4b60-b06b-9012029f6c6c",
                },
            },
            "display_data": {
                "label": "Chat Message",
                "position": {
                    "x": 0.0,
                    "y": 0.0,
                },
                "z_index": 0,
                "icon": "vellum:icon:message",
                "color": "blue",
            },
        }
    ]
