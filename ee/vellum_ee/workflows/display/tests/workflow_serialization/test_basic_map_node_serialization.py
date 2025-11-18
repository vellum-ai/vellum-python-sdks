from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_map_node.workflow import SimpleMapExample


def test_serialize_workflow():
    # GIVEN a Workflow that uses a MapNode
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=SimpleMapExample)
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
                "id": "db2eb237-38e4-417a-8bfc-5bda0f3165ca",
                "key": "fruits",
                "type": "JSON",
                "required": True,
                "default": None,
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
            {
                "id": "145b0b68-224b-4f83-90e6-eea3457e6c3e",
                "key": "final_value",
                "type": "JSON",
            },
        ],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    assert len(workflow_raw_data["edges"]) == 2
    assert len(workflow_raw_data["nodes"]) == 3

    # AND each node should be serialized correctly
    entrypoint_node = workflow_raw_data["nodes"][0]
    assert entrypoint_node == {
        "id": "c0aa464d-1685-4f15-a051-31b426fec92e",
        "type": "ENTRYPOINT",
        "inputs": [],
        "data": {
            "label": "Entrypoint Node",
            "source_handle_id": "844d992e-60ab-4af2-a8ff-52cd858386f7",
        },
        "base": None,
        "definition": None,
        "display_data": {
            "position": {"x": 0.0, "y": -50.0},
        },
    }

    map_node = workflow_raw_data["nodes"][1]

    # AND each edge should be serialized correctly
    serialized_edges = workflow_raw_data["edges"]
    assert not DeepDiff(
        [
            {
                "id": "528eb20a-9db4-4c01-87c0-39b9f5f09753",
                "source_node_id": "c0aa464d-1685-4f15-a051-31b426fec92e",
                "source_handle_id": "844d992e-60ab-4af2-a8ff-52cd858386f7",
                "target_node_id": "f2f94af1-fcbe-497c-80ce-80952c8903c8",
                "target_handle_id": "e16e9d55-5f26-4d89-8c7a-939f1f463d80",
                "type": "DEFAULT",
            },
            {
                "id": "47a34f6e-d139-4702-aa46-6212bb8a150f",
                "source_node_id": "f2f94af1-fcbe-497c-80ce-80952c8903c8",
                "source_handle_id": "aff8a80e-7ce7-43d2-9c9e-9d137efd3b33",
                "target_node_id": "bacc5d55-07d4-4a0a-a69e-831524480de5",
                "target_handle_id": "720dd872-2f3d-47b9-8245-89387f04f300",
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
        "name": "SimpleMapExample",
        "module": [
            "tests",
            "workflows",
            "basic_map_node",
            "workflow",
        ],
    }

    # AND the map node's items input ID should match the subworkflow's items input ID
    items_input_id = map_node["data"]["items_input_id"]
    assert map_node["inputs"][0]["id"] == items_input_id
