from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.web_search.workflow import WebSearchWorkflow


def test_serialize_web_search_workflow():
    # GIVEN a Workflow that uses a WebSearchNode
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=WebSearchWorkflow)

    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND it should have input variables
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 1
    assert input_variables[0]["key"] == "search_query"
    assert input_variables[0]["type"] == "STRING"

    # AND it should have output variables
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 2
    output_keys = {var["key"] for var in output_variables}
    assert output_keys == {"search_results", "result_urls"}

    # AND the web search node should be serialized with GENERIC type
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    nodes = workflow_raw_data["nodes"]

    web_search_node = None
    for node in nodes:
        if node and node.get("type") == "GENERIC":
            base_info = node.get("base", {})
            if base_info and base_info.get("name") == "WebSearchNode":
                web_search_node = node
                break

    assert web_search_node is not None, "WebSearchNode should be serialized as GENERIC type"

    # AND it should have the correct base module reference
    expected_base = {
        "name": "WebSearchNode",
        "module": ["vellum", "workflows", "nodes", "displayable", "web_search_node", "node"],
    }
    assert (
        web_search_node["base"] == expected_base
    ), f"Base mismatch. Expected: {expected_base}, Found: {web_search_node['base']}"

    # AND it should have the serialized attributes (GENERIC nodes use attributes, not inputs)
    web_search_attributes = web_search_node["attributes"]
    attribute_names = {attr["name"] for attr in web_search_attributes}

    # Should include the serializable attributes we defined
    expected_attribute_names = {"query", "api_key", "num_results", "location"}
    assert (
        expected_attribute_names == attribute_names
    ), f"Attributes mismatch. Expected: {expected_attribute_names}, Found: {attribute_names}"

    # AND it should have the expected outputs
    web_search_outputs = web_search_node["outputs"]
    output_names = {output["name"] for output in web_search_outputs}
    expected_output_names = {"text", "urls", "results"}
    assert (
        expected_output_names == output_names
    ), f"Outputs mismatch. Expected: {expected_output_names}, Found: {output_names}"

    # AND it should have proper input value types
    for attr in web_search_attributes:
        if attr["name"] == "query":
            assert attr["value"]["type"] == "WORKFLOW_INPUT", "Query should be workflow input"
        elif attr["name"] == "api_key":
            assert attr["value"]["type"] == "VELLUM_SECRET", "API key should be vellum secret"
        elif attr["name"] in ["num_results", "location"]:
            assert attr["value"]["type"] == "CONSTANT_VALUE", f"{attr['name']} should be constant value"
