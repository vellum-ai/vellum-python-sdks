from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_set_state_node.workflow import BasicSetStateNodeWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a SetStateNode to update chat history
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicSetStateNodeWorkflow)

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its state variables should be what we expect
    state_variables = serialized_workflow["state_variables"]
    assert state_variables == [
        {
            "id": "5102baaa-6413-45b7-828d-11caf56ff489",
            "key": "chat_history",
            "type": "CHAT_HISTORY",
            "default": {"type": "CHAT_HISTORY", "value": []},
            "required": False,
            "extensions": {"color": None},
        },
        {
            "id": "24c5e751-2283-48cc-adff-91d216150aad",
            "key": "counter",
            "type": "NUMBER",
            "default": {"type": "NUMBER", "value": 0.0},
            "required": False,
            "extensions": {"color": None},
        },
    ]

    # AND its raw data should include at least the SetState node
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    set_state_node = next(
        node
        for node in workflow_raw_data["nodes"]
        if node["type"] == "GENERIC" and node["label"] == "Update State Node"
    )

    operations_attribute = next(
        attribute for attribute in set_state_node["attributes"] if attribute["name"] == "operations"
    )

    assert operations_attribute == {
        "id": "6db6c831-c674-4dbb-a8b5-ab505008d15a",
        "name": "operations",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "07ea37d3-64d6-4b0f-a64d-8c55ccebf806",
                    "key": "chat_history",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_STATE", "state_variable_id": "5102baaa-6413-45b7-828d-11caf56ff489"},
                        "operator": "concat",
                        "rhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "140f8146-5ab5-432d-bf1c-3798d0b9ff3e",
                            "node_output_id": "41b0c042-8f67-4667-82c7-754a6b0528d4",
                        },
                    },
                },
                {
                    "id": "271b5fac-a384-403b-857c-79d3872e4dd5",
                    "key": "counter",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_STATE", "state_variable_id": "24c5e751-2283-48cc-adff-91d216150aad"},
                        "operator": "+",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 1.0}},
                    },
                },
            ],
        },
    }
