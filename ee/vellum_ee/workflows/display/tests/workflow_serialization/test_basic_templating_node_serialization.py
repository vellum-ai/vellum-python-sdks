from deepdiff import DeepDiff

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.basic_templating_node.workflow_with_json_input import BasicTemplatingNodeWorkflowWithJson


def test_serialize_workflow():
    # GIVEN a Workflow that uses a vellum templating node",

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=BasicTemplatingNodeWorkflowWithJson)

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
            "id": "f4435f88-703f-40e5-9197-d39b0e43ab72",
            "key": "info",
            "type": "JSON",
            "default": None,
            "required": True,
            "extensions": {"color": None},
            "schema": {},
        }
    ]

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert not DeepDiff(
        [{"id": "62ec9b08-6437-4f8d-bc20-983d317bc348", "key": "result", "type": "JSON"}],
        output_variables,
        ignore_order=True,
    )

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND the templating node should be serialized correctly
    templating_node = next(
        n for n in workflow_raw_data["nodes"] if (n.get("base") or {}).get("name") == "TemplatingNode"
    )

    assert templating_node["id"] == "28ac8611-a755-4d8a-a5c3-520ddd119cf8"
    assert templating_node["type"] == "TEMPLATING"

    assert templating_node["base"]["name"] == "TemplatingNode"
    assert templating_node["base"]["module"] == ["vellum", "workflows", "nodes", "core", "templating_node", "node"]

    assert templating_node["definition"]["name"] == "ExampleTemplatingNode"
    assert templating_node["definition"]["module"] == [
        "tests",
        "workflows",
        "basic_templating_node",
        "workflow_with_json_input",
    ]

    assert templating_node["trigger"]["id"] == "a215a440-cbd9-48ae-a831-be8fa78530a6"
    assert templating_node["trigger"]["merge_behavior"] == "AWAIT_ATTRIBUTES"

    assert len(templating_node["ports"]) == 1
    assert templating_node["ports"][0]["name"] == "default"
    assert templating_node["ports"][0]["type"] == "DEFAULT"

    assert templating_node["data"]["label"] == "Example Templating Node"
    assert templating_node["data"]["output_id"] == "076becd5-f282-40c5-9917-61099e114298"
    assert templating_node["data"]["error_output_id"] is None
    assert templating_node["data"]["source_handle_id"] == "90a2ea33-b08d-46ec-8d9e-612592764268"
    assert templating_node["data"]["target_handle_id"] == "a215a440-cbd9-48ae-a831-be8fa78530a6"
    assert templating_node["data"]["template_node_input_id"] == "7ceb3528-49c6-4f90-b3ef-92b1921a1b7d"
    assert templating_node["data"]["output_type"] == "JSON"

    input_keys = {inp["key"] for inp in templating_node["inputs"]}
    assert "template" in input_keys
    assert "info" in input_keys

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "BasicTemplatingNodeWorkflowWithJson",
        "module": ["tests", "workflows", "basic_templating_node", "workflow_with_json_input"],
    }
