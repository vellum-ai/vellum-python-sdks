from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_default_state.workflow import BasicDefaultStateWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that has a simple state definition
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicDefaultStateWorkflow
    )

    serialized_workflow: dict = workflow_display.serialize()
    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND its input variables should be what we expect
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "0bbe085c-31d3-4b48-b74d-d501f592da90",
                "key": "example",
                "type": "STRING",
                "default": {"type": "STRING", "value": "hello"},
                "required": True,
                "extensions": {"color": None},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its state variables should be what we expect
    state_variables = serialized_workflow["state_variables"]
    assert len(state_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "812ec99b-1859-4361-b795-228628657bac",
                "key": "example",
                "type": "NUMBER",
                "default": {"type": "NUMBER", "value": 5.0},
                "required": False,
                "extensions": {"color": None},
            },
        ],
        state_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    assert not DeepDiff(
        [
            {
                "id": "6e7eeaa5-9559-4ae3-8606-e52ead5805a5",
                "key": "example_input",
                "type": "STRING",
            },
            {
                "id": "e3ae0fe3-7590-4eac-b808-45901d82f2ba",
                "key": "example_state",
                "type": "NUMBER",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
    assert len(workflow_raw_data["edges"]) == 3
    assert len(workflow_raw_data["nodes"]) == 4

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "32684932-7c7c-4b1c-aed2-553de29bf3f7",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "e4136ee4-a51a-4ca3-9a3a-aa96f5de2347",
        },
        "base": None,
        "definition": None,
        "display_data": {
            "position": {"x": 0.0, "y": 0.0},
        },
    }

    final_output_node_state = next(
        n for n in workflow_raw_data["nodes"] if n["type"] == "TERMINAL" and n["data"]["name"] == "example_state"
    )
    final_output_node_input = next(
        n for n in workflow_raw_data["nodes"] if n["type"] == "TERMINAL" and n["data"]["name"] == "example_input"
    )
    assert not DeepDiff(
        {
            "id": "27fdaa45-b8ce-464d-be50-cf71cc56bc10",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "example_state",
                "target_handle_id": "e7a09eb2-c9fb-4d57-b436-9cd9384c8960",
                "output_id": "e3ae0fe3-7590-4eac-b808-45901d82f2ba",
                "output_type": "NUMBER",
                "node_input_id": "8de6a408-cf76-4d04-9845-f75211b611be",
            },
            "inputs": [
                {
                    "id": "8de6a408-cf76-4d04-9845-f75211b611be",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                    "output_id": "84b59a1a-82bf-46bb-9826-9b393402d0fe",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "FinalOutputNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        final_output_node_state,
    )

    assert not DeepDiff(
        {
            "id": "ca8bb585-c9a8-4bf7-bf9d-534b600fe23b",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "example_input",
                "target_handle_id": "8a4a7efd-0e18-43ed-ba32-803e22e3ba0a",
                "output_id": "6e7eeaa5-9559-4ae3-8606-e52ead5805a5",
                "output_type": "STRING",
                "node_input_id": "796b4a0b-da10-403a-acc3-8ebd3ebd3667",
            },
            "inputs": [
                {
                    "id": "796b4a0b-da10-403a-acc3-8ebd3ebd3667",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                                    "output_id": "f305c61e-6e8f-4cea-a53e-92656136b545",
                                },
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "FinalOutputNode",
                "module": ["vellum", "workflows", "nodes", "displayable", "final_output_node", "node"],
            },
            "definition": None,
        },
        final_output_node_input,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "26003bf1-b5a3-41f4-a419-c7ef5a7595df",
                "source_node_id": "32684932-7c7c-4b1c-aed2-553de29bf3f7",
                "source_handle_id": "e4136ee4-a51a-4ca3-9a3a-aa96f5de2347",
                "target_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                "target_handle_id": "6492efcf-4437-4af1-9ad7-269795ccb27a",
                "type": "DEFAULT",
            },
            {
                "id": "b0a57a5f-a1e4-4dc9-85dd-946f08304738",
                "source_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                "source_handle_id": "1e739e86-a285-4438-9725-a152c15a63e3",
                "target_node_id": "ca8bb585-c9a8-4bf7-bf9d-534b600fe23b",
                "target_handle_id": "8a4a7efd-0e18-43ed-ba32-803e22e3ba0a",
                "type": "DEFAULT",
            },
            {
                "id": "e4366583-94a5-40b0-9b6f-1e965695b1fe",
                "source_node_id": "1381c078-efa2-4255-89a1-7b4cb742c7fc",
                "source_handle_id": "1e739e86-a285-4438-9725-a152c15a63e3",
                "target_node_id": "27fdaa45-b8ce-464d-be50-cf71cc56bc10",
                "target_handle_id": "e7a09eb2-c9fb-4d57-b436-9cd9384c8960",
                "type": "DEFAULT",
            },
        ],
        serialized_edges,
        ignore_order=True,
    )

    # AND the display data should be what we expect
    display_data = workflow_raw_data["display_data"]
    assert display_data == {
        "viewport": {
            "x": 0.0,
            "y": 0.0,
            "zoom": 1.0,
        }
    }

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicDefaultStateWorkflow",
        "module": [
            "tests",
            "workflows",
            "basic_default_state",
            "workflow",
        ],
    }
