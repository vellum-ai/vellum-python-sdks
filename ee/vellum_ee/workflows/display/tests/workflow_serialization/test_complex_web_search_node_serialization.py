from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.web_search_complex.workflow import ComplexWebSearchWorkflow


def test_serialize_complex_web_search_workflow():
    # GIVEN a complex Workflow that uses multiple WebSearchNodes
    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=ComplexWebSearchWorkflow)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    # AND it should have the expected input variables
    input_variables = serialized_workflow["input_variables"]
    assert len(input_variables) == 3
    input_keys = {var["key"] for var in input_variables}
    assert input_keys == {"base_query", "result_limit", "search_location"}

    # AND it should have the expected output variables
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 4
    output_keys = {var["key"] for var in output_variables}
    assert output_keys == {"initial_results", "initial_urls", "followup_results", "all_raw_data"}

    # AND the workflow should have multiple web search nodes
    workflow_raw_data = serialized_workflow["workflow_raw_data"]
    nodes = workflow_raw_data["nodes"]

    web_search_nodes = []
    for node in nodes:
        if node and node.get("type") == "GENERIC":
            base_info = node.get("base", {})
            if base_info and base_info.get("name") == "WebSearchNode":
                web_search_nodes.append(node)

    # Should have exactly 2 WebSearchNodes
    assert len(web_search_nodes) == 2, f"Expected 2 WebSearchNodes, found {len(web_search_nodes)}"

    # AND the nodes should be properly connected
    edges = workflow_raw_data["edges"]
    web_search_node_ids = {node["id"] for node in web_search_nodes}

    # Find edge connecting the two WebSearchNodes
    web_search_connections = [
        edge
        for edge in edges
        if edge["source_node_id"] in web_search_node_ids and edge["target_node_id"] in web_search_node_ids
    ]
    assert len(web_search_connections) >= 1, "WebSearchNodes should be connected"

    # AND each node should have different input patterns
    first_node, second_node = web_search_nodes[0], web_search_nodes[1]

    # Test first node attributes (should use workflow inputs and secret)
    first_attrs = {attr["name"]: attr["value"]["type"] for attr in first_node["attributes"]}
    assert first_attrs["query"] == "WORKFLOW_INPUT", "First node query should be workflow input"
    assert first_attrs["api_key"] == "VELLUM_SECRET", "First node api_key should be vellum secret"
    assert first_attrs["num_results"] == "WORKFLOW_INPUT", "First node num_results should be workflow input"
    assert first_attrs["location"] == "WORKFLOW_INPUT", "First node location should be workflow input"

    # Test second node attributes (should use node output, constant, and None)
    second_attrs = {attr["name"]: attr["value"]["type"] for attr in second_node["attributes"]}
    assert second_attrs["query"] == "NODE_OUTPUT", "Second node query should be node output"
    assert second_attrs["api_key"] == "CONSTANT_VALUE", "Second node api_key should be constant"
    assert second_attrs["num_results"] == "CONSTANT_VALUE", "Second node num_results should be constant"
    assert second_attrs["location"] == "CONSTANT_VALUE", "Second node location should be constant (None)"

    # AND all nodes should have consistent output structure
    for node in web_search_nodes:
        outputs = node["outputs"]
        output_names = {output["name"] for output in outputs}
        expected_output_names = {"text", "urls", "results"}
        assert expected_output_names == output_names, f"Node outputs mismatch: {output_names}"
