from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_generic_node.workflow import BasicGenericNodeWorkflow


def test_serialize_workflow():
    # GIVEN a Workflow that uses a generic node
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicGenericNodeWorkflow)

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

    # AND the generic node should be serialized correctly
    generic_node = next(n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "BaseNode")
    assert generic_node["id"] == "bf98371c-65d3-43c1-99a2-0f5369397847"

    # AND the nodes should have been auto-positioned since they all started at (0,0)
    nodes = workflow_raw_data["nodes"]
    positions = [node["display_data"]["position"] for node in nodes]

    nodes_at_zero = sum(1 for pos in positions if pos["x"] == 0.0 and pos["y"] == 0.0)
    assert nodes_at_zero < len(nodes), "Auto layout should have positioned nodes away from (0,0)"

    x_positions = [pos["x"] for pos in positions]
    assert all(x >= 0 for x in x_positions), "All x positions should be non-negative"
    assert len(set(x_positions)) > 1 or len(nodes) == 1, "Nodes should be spread across different x positions"

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicGenericNodeWorkflow",
        "module": ["tests", "workflows", "basic_generic_node", "workflow"],
    }
