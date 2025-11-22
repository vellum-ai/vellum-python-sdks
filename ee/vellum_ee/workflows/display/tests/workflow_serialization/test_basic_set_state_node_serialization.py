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
            "id": "948a902d-248d-4b00-8bf4-cdd202302f20",
            "key": "chat_history",
            "type": "CHAT_HISTORY",
            "default": {"type": "CHAT_HISTORY", "value": []},
            "required": False,
            "extensions": {"color": None},
        },
        {
            "id": "396a06f5-21da-4769-831a-d4fd613029ae",
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
        "id": "933beba4-7455-4563-a447-b0d06e3d2589",
        "name": "operations",
        "value": {
            "type": "DICTIONARY_REFERENCE",
            "entries": [
                {
                    "id": "6caeb2fb-c634-4cad-a97c-fc444cbaa6fb",
                    "key": "chat_history",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_STATE", "state_variable_id": "948a902d-248d-4b00-8bf4-cdd202302f20"},
                        "operator": "concat",
                        "rhs": {
                            "type": "NODE_OUTPUT",
                            "node_id": "32f69de2-53e8-4151-b036-4e831669cf1d",
                            "node_output_id": "611ad55f-6c6d-420b-b5a2-b50a06812254",
                        },
                    },
                },
                {
                    "id": "04964b4f-65bc-436e-943d-fef8b5d0dc60",
                    "key": "counter",
                    "value": {
                        "type": "BINARY_EXPRESSION",
                        "lhs": {"type": "WORKFLOW_STATE", "state_variable_id": "396a06f5-21da-4769-831a-d4fd613029ae"},
                        "operator": "+",
                        "rhs": {"type": "CONSTANT_VALUE", "value": {"type": "NUMBER", "value": 1.0}},
                    },
                },
            ],
        },
    }
