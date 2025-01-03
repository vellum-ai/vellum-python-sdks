from unittest import mock

from deepdiff import DeepDiff

from vellum_ee.workflows.display.nodes.base_node_vellum_display import BaseNodeVellumDisplay
from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_error_node.workflow import BasicErrorNodeWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow with an error node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicErrorNodeWorkflow
    )

    # TODO: Support serialization of BaseNode
    # https://app.shortcut.com/vellum/story/4871/support-serialization-of-base-node
    with mock.patch.object(BaseNodeVellumDisplay, "serialize") as mocked_serialize:
        mocked_serialize.return_value = {"type": "MOCKED"}
        serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
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
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
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
        "definition": {
            "name": "BaseNode",
            "module": ["vellum", "workflows", "nodes", "bases", "base"],
            "bases": [],
        },
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
            "inputs": [],
            "data": {
                "name": "error-node",
                "label": "Fail Node",
                "target_handle_id": "70c19f1c-309c-4a5d-ba65-664c0bb2fedf",
                "error_source_input_id": "None",
                "error_output_id": "None",
            },
            "display_data": {"position": {"x": 0.0, "y": 0.0}},
            "definition": {
                "name": "FailNode",
                "module": ["tests", "workflows", "basic_error_node", "workflow"],
                "bases": [
                    {
                        "name": "ErrorNode",
                        "module": [
                            "vellum",
                            "workflows",
                            "nodes",
                            "core",
                            "error_node",
                            "node",
                        ],
                    }
                ],
            },
        },
        error_node,
        ignore_order=True,
    )

    mocked_base_nodes = [
        node
        for i, node in enumerate(workflow_raw_data["nodes"])
        if i != error_index and i != 0 and i != len(workflow_raw_data["nodes"]) - 1
    ]

    assert not DeepDiff(
        [
            {
                "type": "MOCKED",
            },
            {
                "type": "MOCKED",
            },
        ],
        mocked_base_nodes,
    )

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
                "node_input_id": "39ff42c9-eae8-432e-ad41-e208fba77027",
            },
            "inputs": [
                {
                    "id": "39ff42c9-eae8-432e-ad41-e208fba77027",
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
            "definition": {
                "name": "FinalOutputNode",
                "module": [
                    "vellum",
                    "workflows",
                    "nodes",
                    "displayable",
                    "final_output_node",
                    "node",
                ],
                "bases": [
                    {
                        "name": "BaseNode",
                        "module": ["vellum", "workflows", "nodes", "bases", "base"],
                        "bases": [],
                    }
                ],
            },
        },
        terminal_node,
    )
