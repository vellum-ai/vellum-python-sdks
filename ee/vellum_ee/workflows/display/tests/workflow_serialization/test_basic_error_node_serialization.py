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
                "schema": {"type": "integer"},
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

    # AND the error node should be serialized correctly
    error_node = next(n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "ErrorNode")

    assert error_node["id"] == "98597c0e-8951-4320-98ed-efd7f79c00cf"
    assert error_node["type"] == "ERROR"

    assert error_node["base"]["name"] == "ErrorNode"
    assert error_node["base"]["module"] == ["vellum", "workflows", "nodes", "core", "error_node", "node"]

    assert error_node["definition"]["name"] == "FailNode"
    assert error_node["definition"]["module"] == ["tests", "workflows", "basic_error_node", "workflow"]

    assert error_node["trigger"]["id"] == "865dcf9c-8fe8-44c0-bf36-2c92eb47927e"
    assert error_node["trigger"]["merge_behavior"] == "AWAIT_ATTRIBUTES"

    assert error_node["ports"] == []

    assert error_node["data"]["label"] == "Fail Node"
    assert error_node["data"]["target_handle_id"] == "865dcf9c-8fe8-44c0-bf36-2c92eb47927e"
    assert error_node["data"]["error_source_input_id"] == "f7fc097f-db5b-48c1-8c33-391834678521"

    assert len(error_node["inputs"]) == 1
    assert error_node["inputs"][0]["key"] == "error_source_input_id"

    passthrough_nodes = [node for node in workflow_raw_data["nodes"] if node["type"] == "GENERIC"]
    assert len(passthrough_nodes) == 2
