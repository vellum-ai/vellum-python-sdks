from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.map_node_with_terminal_nodes.workflow import MapNodeWithTerminalNodes


def test_serialize_workflow__terminal_nodes_have_different_output_ids():
    """
    Tests that terminal nodes with the same base class serialize to different output IDs
    when one is at the top level and one is inside a map node.
    """

    # WHEN we serialize it
    workflow_display = get_workflow_display(workflow_class=MapNodeWithTerminalNodes)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation of the Workflow
    assert serialized_workflow.keys() == {
        "workflow_raw_data",
        "input_variables",
        "state_variables",
        "output_variables",
    }

    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    map_node = None
    top_level_terminal_node = None

    for node in workflow_raw_data["nodes"]:
        if node["type"] == "MAP":
            map_node = node
        elif node["type"] == "TERMINAL":
            top_level_terminal_node = node

    assert map_node is not None, "Map node should be present"
    assert top_level_terminal_node is not None, "Top-level terminal node should be present"

    subworkflow_raw_data = map_node["data"]["workflow_raw_data"]
    map_terminal_node = None

    for node in subworkflow_raw_data["nodes"]:
        if node["type"] == "TERMINAL":
            map_terminal_node = node
            break

    assert map_terminal_node is not None, "Terminal node inside map should be present"

    assert top_level_terminal_node["base"]["name"] == "FinalOutputNode", (
        f"Top-level terminal should have base name 'FinalOutputNode', " f"got {top_level_terminal_node['base']['name']}"
    )
    assert map_terminal_node["base"]["name"] == "FinalOutputNode", (
        f"Map terminal should have base name 'FinalOutputNode', " f"got {map_terminal_node['base']['name']}"
    )

    # THEN the top-level terminal node and the map's terminal node should have different output IDs
    top_level_output_id = top_level_terminal_node["data"]["output_id"]
    map_terminal_output_id = map_terminal_node["data"]["output_id"]

    assert top_level_output_id != map_terminal_output_id, (
        f"Terminal nodes should have different output IDs. "
        f"Top-level: {top_level_output_id}, Map terminal: {map_terminal_output_id}"
    )
