from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_error_node.workflow import BasicErrorNodeWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow with an error node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicErrorNodeWorkflow)

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
                "id": "5d9edd44-b35b-4bad-ad51-ccdfe8185ff5",
                "key": "threshold",
                "type": "NUMBER",
                "default": None,
                "required": True,
                "extensions": {"color": None},
            }
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [
            {
                "id": "04c5c6be-f5e1-41b8-b668-39e179790d9e",
                "key": "final_value",
                "type": "NUMBER",
            }
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 4
    assert len(workflow_raw_data["nodes"]) == 5

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "10e90662-e998-421d-a5c9-ec16e37a8de1",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "7d86498b-84ed-4feb-8e62-2188058c2c4e",
        },
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    error_node, error_index = next(
        (
            (node, index)
            for index, node in enumerate(workflow_raw_data["nodes"])
            if node.get("data", {}).get("label") == "Fail Node"
        ),
        (None, None),
    )
    assert not DeepDiff(
        {
            "id": "5cf9c5e3-0eae-4daf-8d73-8b9536258eb9",
            "type": "ERROR",
            "inputs": [
                {
                    "id": "8e4c8d76-2e02-4d7e-a7bf-d71af392dc49",
                    "key": "error_source_input_id",
                    "value": {
                        "rules": [
                            {
                                "type": "CONSTANT_VALUE",
                                "data": {"type": "STRING", "value": "Input threshold was too low"},
                            }
                        ],
                        "combinator": "OR",
                    },
                }
            ],
            "data": {
                "label": "Fail Node",
                "target_handle_id": "70c19f1c-309c-4a5d-ba65-664c0bb2fedf",
                "error_source_input_id": "8e4c8d76-2e02-4d7e-a7bf-d71af392dc49",
            },
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "base": {
                "name": "ErrorNode",
                "module": ["vellum", "workflows", "nodes", "core", "error_node", "node"],
            },
            "definition": {
                "name": "FailNode",
                "module": ["tests", "workflows", "basic_error_node", "workflow"],
            },
        },
        error_node,
        ignore_order=True,
    )

    passthrough_nodes = [node for node in workflow_raw_data["nodes"] if node["type"] == "GENERIC"]
    assert len(passthrough_nodes) == 2

    terminal_node = workflow_raw_data["nodes"][-1]
    assert not DeepDiff(
        {
            "id": "e5fff999-80c7-4cbc-9d99-06c653f3ec77",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "final_value",
                "target_handle_id": "b070e9bc-e9b7-46d3-8f5b-0b646bd25cf0",
                "output_id": "04c5c6be-f5e1-41b8-b668-39e179790d9e",
                "output_type": "NUMBER",
                "node_input_id": "c191a5c1-8912-49ad-bf4b-c6d4d58ed482",
            },
            "inputs": [
                {
                    "id": "c191a5c1-8912-49ad-bf4b-c6d4d58ed482",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "1eee9b4e-531f-45f2-a4b9-42207fac2c33",
                                    "output_id": "c6b017a4-25e9-4296-8d81-6aa4b3dad171",
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
                "module": [
                    "vellum",
                    "workflows",
                    "nodes",
                    "displayable",
                    "final_output_node",
                    "node",
                ],
            },
            "definition": None,
        },
        terminal_node,
    )
