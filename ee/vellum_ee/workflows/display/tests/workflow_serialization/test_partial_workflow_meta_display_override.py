"""Tests for partial WorkflowMetaDisplay override serialization."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.base import WorkflowDisplayData, WorkflowDisplayDataViewport, WorkflowMetaDisplay
from vellum_ee.workflows.display.workflows.base_workflow_display import BaseWorkflowDisplay
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_triggerless_workflow_with_partial_display_override_creates_entrypoint():
    """
    Tests that a triggerless workflow with partial WorkflowMetaDisplay overrides
    (only display_data set) still creates an ENTRYPOINT node with backfilled IDs.
    """

    # GIVEN a simple triggerless workflow
    class ProcessNode(BaseNode):
        pass

    class TestWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = ProcessNode

    # AND a display class that only overrides display_data (viewport), not entrypoint IDs
    class TestWorkflowDisplay(BaseWorkflowDisplay[TestWorkflow]):
        workflow_display = WorkflowMetaDisplay(
            display_data=WorkflowDisplayData(viewport=WorkflowDisplayDataViewport(x=100.0, y=200.0, zoom=1.5))
        )

    # WHEN we serialize the workflow
    result = get_workflow_display(workflow_class=TestWorkflow).serialize()

    # THEN the workflow should have an ENTRYPOINT node
    workflow_raw_data = result["workflow_raw_data"]
    assert isinstance(workflow_raw_data, dict)
    nodes = workflow_raw_data["nodes"]
    assert isinstance(nodes, list)
    entrypoint_nodes = [n for n in nodes if isinstance(n, dict) and n.get("type") == "ENTRYPOINT"]
    assert len(entrypoint_nodes) == 1, "Triggerless workflow with partial overrides should have an ENTRYPOINT node"

    # AND the ENTRYPOINT node should have valid IDs (not None)
    entrypoint_node = entrypoint_nodes[0]
    assert isinstance(entrypoint_node, dict)
    assert entrypoint_node["id"] is not None, "ENTRYPOINT node should have a non-None id"
    entrypoint_data = entrypoint_node["data"]
    assert isinstance(entrypoint_data, dict)
    source_handle_id = entrypoint_data["source_handle_id"]
    assert source_handle_id is not None, "ENTRYPOINT node should have a non-None source_handle_id"

    # AND there should be an edge from ENTRYPOINT to the process node
    edges = workflow_raw_data["edges"]
    assert isinstance(edges, list)
    entrypoint_edges = [e for e in edges if isinstance(e, dict) and e.get("source_node_id") == entrypoint_node["id"]]
    assert len(entrypoint_edges) > 0, "Should have edges from ENTRYPOINT node"
