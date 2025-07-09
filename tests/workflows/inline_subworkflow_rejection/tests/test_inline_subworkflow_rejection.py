from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.inline_subworkflow_rejection.workflow import InlineSubworkflowRejectionWorkflow


def test_run_workflow__inline_subworkflow_rejection():
    """
    Tests that an InlineSubworkflowNode properly propagates rejection events from its subworkflow.
    """

    workflow = InlineSubworkflowRejectionWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete with a rejection event
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    assert terminal_event.error.code == WorkflowErrorCode.USER_DEFINED_ERROR
    assert terminal_event.error.message == "Subworkflow node intentionally failed"
