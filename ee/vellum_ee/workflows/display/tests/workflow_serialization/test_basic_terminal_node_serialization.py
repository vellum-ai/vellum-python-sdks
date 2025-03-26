from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_final_output_node.workflow import BasicFinalOutputNodeWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a Final Output Node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicFinalOutputNodeWorkflow
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
    assert input_variables == [
        {
            "id": "e39a7b63-de15-490a-ae9b-8112c767aea0",
            "key": "input",
            "type": "STRING",
            "required": True,
            "default": None,
            "extensions": {"color": None},
        }
    ]

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables == [
        {
            "id": "a34cd21e-40e5-47f4-8fdb-910593f3e9e2",
            "key": "value",
            "type": "STRING",
        }
    ]

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
    assert len(workflow_raw_data["edges"]) == 1
    assert len(workflow_raw_data["nodes"]) == 2

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "631e2789-d60d-4088-9e3a-0ea93517075b",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "8b8d52a2-844f-44fe-a6c4-142fa70d391b"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    final_output_node = workflow_raw_data["nodes"][1]
    assert final_output_node == {
        "id": "620ec17b-e330-4212-b619-3c39dc63fb22",
        "type": "TERMINAL",
        "data": {
            "label": "Basic Final Output Node",
            "name": "basic-final-output-node",
            "target_handle_id": "0173d3c6-11d1-44b7-b070-ca9ff5119046",
            "output_id": "97349956-d228-4b51-a64b-1331f788373f",
            "output_type": "STRING",
            "node_input_id": "5322567a-f40c-400a-96b3-c3b054db543e",
        },
        "inputs": [
            {
                "id": "5322567a-f40c-400a-96b3-c3b054db543e",
                "key": "node_input",
                "value": {
                    "rules": [
                        {
                            "type": "INPUT_VARIABLE",
                            "data": {"input_variable_id": "e39a7b63-de15-490a-ae9b-8112c767aea0"},
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
        "definition": {
            "name": "BasicFinalOutputNode",
            "module": ["tests", "workflows", "basic_final_output_node", "workflow"],
        },
        "outputs": [
            {
                "id": "97349956-d228-4b51-a64b-1331f788373f",
                "name": "value",
                "type": "STRING",
                "value": {"type": "WORKFLOW_INPUT", "input_variable_id": "e39a7b63-de15-490a-ae9b-8112c767aea0"},
            }
        ],
    }
