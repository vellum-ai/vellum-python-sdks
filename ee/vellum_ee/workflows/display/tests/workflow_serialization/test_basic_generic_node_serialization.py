from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows import VellumWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_generic_node.workflow import BasicGenericNodeWorkflow


def test_serialize_workflow(vellum_client):
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(
        base_display_class=VellumWorkflowDisplay, workflow_class=BasicGenericNodeWorkflow
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
                "id": "a07c2273-34a7-42b5-bcad-143b6127cc8a",
                "key": "input",
                "type": "STRING",
                "default": None,
                "required": True,
                "extensions": {"color": None},
            },
        ],
        input_variables,
        ignore_order=True,
    )

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [
            {"id": "2b6389d0-266a-4be4-843e-4e543dd3d727", "key": "output", "type": "STRING"},
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert workflow_raw_data.keys() == {"edges", "nodes", "display_data", "definition"}
    assert len(workflow_raw_data["edges"]) == 2
    assert len(workflow_raw_data["nodes"]) == 3

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "f1e4678f-c470-400b-a40e-c8922cc99a86",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {"label": "Entrypoint Node", "source_handle_id": "40201804-8beb-43ad-8873-a027759512f1"},
        "display_data": {"position": {"x": 0.0, "y": 0.0}},
        "base": None,
        "definition": None,
    }

    api_node = workflow_raw_data["nodes"][1]
    assert api_node["id"] == "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f"

    final_output_node = workflow_raw_data["nodes"][2]
    assert not DeepDiff(
        {
            "id": "50e3b446-afcd-4a5d-8c6f-5f05eaf2200e",
            "type": "TERMINAL",
            "data": {
                "label": "Final Output",
                "name": "output",
                "target_handle_id": "8bd9f4f3-9f66-4d95-8e84-529b0002c531",
                "output_id": "2b6389d0-266a-4be4-843e-4e543dd3d727",
                "output_type": "STRING",
                "node_input_id": "545d6001-cfb5-4ccc-bcdf-3b03ccd67d90",
            },
            "inputs": [
                {
                    "id": "545d6001-cfb5-4ccc-bcdf-3b03ccd67d90",
                    "key": "node_input",
                    "value": {
                        "rules": [
                            {
                                "type": "NODE_OUTPUT",
                                "data": {
                                    "node_id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
                                    "output_id": "0a9c7a80-fc89-4a71-aac0-66489e4ddb85",
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
        final_output_node,
        ignore_order=True,
    )

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "445dd2de-82b2-482b-89f6-5f49d8eb21a9",
                "source_node_id": "f1e4678f-c470-400b-a40e-c8922cc99a86",
                "source_handle_id": "40201804-8beb-43ad-8873-a027759512f1",
                "target_node_id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
                "target_handle_id": "b7bfb298-959a-4d2b-8b85-bbd0d2522703",
                "type": "DEFAULT",
            },
            {
                "id": "b741c861-cf67-4649-b9ef-b43a4add72b1",
                "source_node_id": "c2ed23f7-f6cb-4a56-a91c-2e5f9d8fda7f",
                "source_handle_id": "89dccfa5-cc1a-4612-bd87-86cb444f6dd4",
                "target_node_id": "50e3b446-afcd-4a5d-8c6f-5f05eaf2200e",
                "target_handle_id": "8bd9f4f3-9f66-4d95-8e84-529b0002c531",
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
        "name": "BasicGenericNodeWorkflow",
        "module": ["tests", "workflows", "basic_generic_node", "workflow"],
    }
