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
    THEN we should get a serialized representation without errors
    """
    workflow_display = get_workflow_display(workflow_class=ParallelNodesWithPorts)
    serialized_workflow: dict = workflow_display.serialize()

    # THEN we should get a serialized representation without errors
    errors = serialized_workflow.get("errors", [])
    assert len(errors) == 0
