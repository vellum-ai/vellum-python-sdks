from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_trigger_slack.workflow import SlackTriggerWorkflow


def test_serialize_slack_trigger_workflow():
    workflow_display = get_workflow_display(workflow_class=SlackTriggerWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
        "triggers",
    }

    triggers = serialized_workflow["triggers"]
    assert triggers == [
        {
            "id": "45855aa4-27a0-426b-b399-a8ff2932a684",
            "type": "SLACK_MESSAGE",
            "attributes": [
                {"id": "9d4bd7d7-314d-48b8-a483-f964ac3ca28a", "name": "channel", "type": "STRING", "value": None},
                {"id": "af4aac3c-74f2-4250-801b-f2dbd7745277", "name": "event_type", "type": "STRING", "value": None},
                {"id": "bdf8965f-b2f1-4f83-9a5a-e1532d73c795", "name": "message", "type": "STRING", "value": None},
                {"id": "5a910518-f875-497c-ab5f-680eecce2d1d", "name": "thread_ts", "type": "STRING", "value": None},
                {"id": "4aadb9ec-aabf-4a58-a9bb-41e89e8a20cb", "name": "timestamp", "type": "STRING", "value": None},
                {"id": "c16971a0-73a3-4b81-93dc-2bcaafa3585a", "name": "user", "type": "STRING", "value": None},
            ],
        }
    ]

    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    nodes = workflow_raw_data["nodes"]

    process_node = next(node for node in nodes if node["type"] == "GENERIC" and node["label"] == "Process Message Node")
    assert "outputs" in process_node
    assert process_node["outputs"] == [
        {
            "id": "a1208db6-2daf-48a4-acee-71c8b1f42656",
            "name": "processed_message",
            "type": "STRING",
            "value": {
                "type": "TRIGGER_ATTRIBUTE",
                "trigger_id": "45855aa4-27a0-426b-b399-a8ff2932a684",
                "attribute_id": "bdf8965f-b2f1-4f83-9a5a-e1532d73c795",
            },
        }
    ]

    assert triggers[0]["id"] == process_node["outputs"][0]["value"]["trigger_id"]
