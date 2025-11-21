"""
Test serialization of {A, B} >> {C, D} graph pattern from APO-2222.

This test verifies that workflows using the pattern where two nodes execute in
parallel and feed into a node with ports serialize correctly.
"""

from deepdiff import DeepDiff

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
    assert not DeepDiff(
        [
            {
                "id": "db2eb237-38e4-417a-8bfc-5bda0f3165ca",
                "key": "value_a",
                "type": "STRING",
                "required": True,
                "default": None,
                "extensions": {"color": None},
            },
            {
                "id": "db2eb237-38e4-417a-8bfc-5bda0f3165cb",
                "key": "value_b",
                "type": "STRING",
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
                "key": "final_result",
                "type": "STRING",
            },
        ],
        output_variables,
        ignore_order=True,
    )

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
    node_names = {(n.get("base") or {}).get("name") for n in nodes}
    assert node_names == {"NodeA", "NodeB", "NodeC", "NodeD", "NodeE", "FinalNode"}

    node_c = next(n for n in nodes if (n.get("base") or {}).get("name") == "NodeC")
    assert "ports" in node_c["data"]
    ports = node_c["data"]["ports"]
    assert len(ports) == 2
    port_names = {p["name"] for p in ports}
    assert port_names == {"path_one", "path_two"}

    edges = workflow_raw_data["edges"]

    edges_to_c = [e for e in edges if e["target_node_id"] == node_c["id"]]
    assert len(edges_to_c) >= 2  # At least one from A and one from B

    edges_from_c = [e for e in edges if e["source_node_id"] == node_c["id"]]
    assert len(edges_from_c) >= 2  # One to D, one to E

    final_node = next(n for n in nodes if (n.get("base") or {}).get("name") == "FinalNode")
    edges_to_final = [e for e in edges if e["target_node_id"] == final_node["id"]]
    assert len(edges_to_final) >= 2  # One from D, one from E
