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

    # AND each node should be serialized correctly

    map_node = next(n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "MapNode")

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
