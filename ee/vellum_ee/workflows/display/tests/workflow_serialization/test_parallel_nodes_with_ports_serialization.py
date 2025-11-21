"""
Test serialization of {A, B} >> {C, D} graph pattern from APO-2222.

This test verifies that workflows using the pattern where two nodes execute in
parallel and feed into a node with ports serialize correctly.
"""

from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display

from tests.workflows.parallel_nodes_with_ports.workflow import ParallelNodesWithPorts


def test_serialize_parallel_nodes_with_ports():
    """
    Test serialization of workflow with {A, B} >> {C, D} pattern.

    GIVEN a Workflow that uses the pattern {NodeA, NodeB} >> {NodeC.Ports.path_one >> NodeD, ...}
    WHEN we serialize it
    THEN we should get a correct serialized representation with all nodes and edges properly connected
    """
    workflow_display = get_workflow_display(workflow_class=ParallelNodesWithPorts)
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
    assert len(input_variables) == 2

    input_keys = {var["key"] for var in input_variables}
    assert input_keys == {"value_a", "value_b"}

    for var in input_variables:
        assert var["type"] == "STRING"
        assert var["required"] is True
        assert var["default"] is None
        assert "id" in var  # ID exists but is dynamically generated

    # AND its output variables should be what we expect
    output_variables = serialized_workflow["output_variables"]
    assert len(output_variables) == 1
    assert output_variables[0]["key"] == "final_result"
    assert output_variables[0]["type"] == "STRING"
    assert "id" in output_variables[0]

    # AND its raw data should be what we expect
    workflow_raw_data = serialized_workflow["workflow_raw_data"]

    # AND the definition should be what we expect
    definition = workflow_raw_data["definition"]
    assert definition == {
        "name": "ParallelNodesWithPorts",
        "module": [
            "tests",
            "workflows",
            "parallel_nodes_with_ports",
            "workflow",
        ],
    }

    nodes = workflow_raw_data["nodes"]
    assert len(nodes) > 0

    edges = workflow_raw_data["edges"]
    assert len(edges) > 0

    # AND the graph structure should show fan-in and fan-out pattern
    node_ids = {n["id"] for n in nodes}
    in_degree = {node_id: 0 for node_id in node_ids}
    out_degree = {node_id: 0 for node_id in node_ids}

    for edge in edges:
        source_id = edge["source_node_id"]
        target_id = edge["target_node_id"]
        if source_id in out_degree:
            out_degree[source_id] += 1
        if target_id in in_degree:
            in_degree[target_id] += 1

    nodes_with_multiple_inputs = [node_id for node_id, degree in in_degree.items() if degree >= 2]
    assert len(nodes_with_multiple_inputs) > 0

    nodes_with_multiple_outputs = [node_id for node_id, degree in out_degree.items() if degree >= 2]
    assert len(nodes_with_multiple_outputs) > 0
