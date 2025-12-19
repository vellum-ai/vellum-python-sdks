"""Tests for ChatMessageTrigger serialization."""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.chat_message_trigger_execution.workflows.simple_chat_workflow import SimpleChatWorkflow


def test_simple_chat_workflow_serialization():
    """SimpleChatWorkflow from tests/workflows serializes correctly with ChatMessageTrigger."""

    # WHEN we serialize the SimpleChatWorkflow
    workflow_display = get_workflow_display(workflow_class=SimpleChatWorkflow)
    result: dict = workflow_display.serialize()

    # THEN the triggers should be serialized correctly
    assert result["triggers"] == [
        {
            "id": "9e14c49b-c6d9-4fe5-9ff2-835fd695fe5f",
            "type": "CHAT_MESSAGE",
            "attributes": [
                {
                    "id": "5edbfd78-b634-4305-b2ad-d9feecbd5e5f",
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
