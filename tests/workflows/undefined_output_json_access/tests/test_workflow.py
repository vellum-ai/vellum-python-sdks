from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.undefined_output_json_access.workflow import UndefinedOutputJsonAccessWorkflow


def test_run_workflow__undefined_output_json_access():
    """
    Tests that accessing a field on an undefined output returns a proper rejection event.
    """

    workflow = UndefinedOutputJsonAccessWorkflow()

    # WHEN the workflow is streamed with all events
    events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # THEN the workflow should complete with a rejection event
    workflow_rejected_event = events[-1]
    assert workflow_rejected_event.name == "workflow.execution.rejected", workflow_rejected_event

    # AND the error code should indicate a node execution error
    assert workflow_rejected_event.error.code == WorkflowErrorCode.NODE_EXECUTION

    # AND the error message should indicate the issue with accessing a field on undefined
    assert "Cannot get field" in workflow_rejected_event.error.message
    assert "field" in workflow_rejected_event.error.message

    # AND the node should also have a rejection event
    node_rejected_event = events[-2]
    assert node_rejected_event.name == "node.execution.rejected"

    # AND the node rejection should have the same error details
    assert node_rejected_event.error.code == WorkflowErrorCode.NODE_EXECUTION
    assert "Cannot get field" in node_rejected_event.error.message
