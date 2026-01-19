"""Tests for validation when a workflow has no triggers and no entrypoint node."""

from vellum.workflows import BaseWorkflow
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.bases.base import BaseNode
from vellum.workflows.state.base import BaseState
from vellum_ee.workflows.display.utils.exceptions import WorkflowValidationError
from vellum_ee.workflows.display.workflows.get_vellum_workflow_display_class import get_workflow_display


def test_workflow_serialization_error__no_triggers_no_entrypoint():
    """
    Tests that serialization adds an error when a workflow has no triggers and no entrypoint node.
    """

    # GIVEN a workflow with an empty graph (no triggers and no entrypoint nodes)
    class EmptyWorkflow(BaseWorkflow[BaseInputs, BaseState]):
        graph = set()

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=EmptyWorkflow)
    workflow_display.serialize()

    # THEN the display_context should contain a WorkflowValidationError
    errors = list(workflow_display.display_context.errors)
    validation_errors = [e for e in errors if isinstance(e, WorkflowValidationError)]
    assert len(validation_errors) == 1

    # AND the error message should be exact and descriptive
    error = validation_errors[0]
    assert str(error) == (
        "Workflow validation error in EmptyWorkflow: "
        "Workflow has no triggers and no entrypoint nodes. "
        "A workflow must have at least one trigger or one node in its graph."
    )


def test_workflow_serialization_error__no_triggers_no_entrypoint_with_unused_graphs():
    """
    Tests that serialization adds an error even when a workflow has nodes in unused_graphs
    but no triggers and no entrypoint nodes in the main graph.
    """

    # GIVEN a workflow with nodes only in unused_graphs (no triggers and no entrypoint nodes in main graph)
    class UnusedNode(BaseNode):
        class Outputs(BaseNode.Outputs):
            result: str

    class WorkflowWithOnlyUnusedGraphs(BaseWorkflow[BaseInputs, BaseState]):
        graph = set()
        unused_graphs = {UnusedNode}

    # WHEN we serialize the workflow
    workflow_display = get_workflow_display(workflow_class=WorkflowWithOnlyUnusedGraphs)
    workflow_display.serialize()

    # THEN the display_context should contain a WorkflowValidationError
    errors = list(workflow_display.display_context.errors)
    validation_errors = [e for e in errors if isinstance(e, WorkflowValidationError)]
    assert len(validation_errors) == 1

    # AND the error message should indicate the workflow has no triggers and no entrypoint nodes
    error = validation_errors[0]
    assert "no triggers and no entrypoint nodes" in str(error)
