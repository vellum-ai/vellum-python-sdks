from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.web_search.workflow import WebSearchWorkflow


def test_serialize_web_search_workflow():
    # GIVEN a WebSearchWorkflow with a node that has various input types
    # - query from workflow input
    # - api_key from VellumSecretReference
    # - num_results as a constant integer
    # - location as a constant string

    # WHEN we serialize the workflow through the display system
    workflow_display = get_workflow_display(workflow_class=WebSearchWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a properly structured serialized workflow
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

    # AND the web search node should be serialized as a GENERIC type node
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    nodes = workflow_raw_data["nodes"]

    web_search_node = next(
        (
            node
            for node in nodes
            if node and node.get("type") == "GENERIC" and node.get("base", {}).get("name") == "WebSearchNode"
        ),
        None,
    )

    assert web_search_node is not None, "WebSearchNode should be serialized as GENERIC type"

    # AND it should have the correct base module reference
    expected_base = {
        "name": "WebSearchNode",
        "module": ["vellum", "workflows", "nodes", "displayable", "web_search_node", "node"],
    }
    assert (
        web_search_node["base"] == expected_base
    ), f"Base mismatch. Expected: {expected_base}, Found: {web_search_node['base']}"

    # AND it should have all four serializable attributes defined in our display class
    web_search_attributes = web_search_node["attributes"]
    attribute_names = {attr["name"] for attr in web_search_attributes}

    # AND the attributes should match exactly what we defined in __serializable_inputs__
    expected_attribute_names = {"query", "api_key", "num_results", "location"}
    assert (
        expected_attribute_names == attribute_names
    ), f"Attributes mismatch. Expected: {expected_attribute_names}, Found: {attribute_names}"

    # AND it should have all three expected outputs from WebSearchNode
    web_search_outputs = web_search_node["outputs"]
    output_names = {output["name"] for output in web_search_outputs}
    expected_output_names = {"text", "urls", "results"}
    assert (
        expected_output_names == output_names
    ), f"Outputs mismatch. Expected: {expected_output_names}, Found: {output_names}"

    # AND each attribute should have the correct value type based on its source
    for attr in web_search_attributes:
        if attr["name"] == "query":
            # AND query should reference the workflow input
            assert attr["value"]["type"] == "WORKFLOW_INPUT", "Query should be workflow input"
        elif attr["name"] == "api_key":
            # AND api_key should reference a Vellum secret
            assert attr["value"]["type"] == "VELLUM_SECRET", "API key should be vellum secret"
        elif attr["name"] in ["num_results", "location"]:
            # AND num_results and location should be constant values
            assert attr["value"]["type"] == "CONSTANT_VALUE", f"{attr['name']} should be constant value"
