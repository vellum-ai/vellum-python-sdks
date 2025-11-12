from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.undefined_output_json_access.workflow import UndefinedOutputJsonAccessWorkflow


def test_run_workflow__undefined_output_json_access():
    """
    Tests that accessing a field on an undefined output returns a proper rejection event.
    """

    workflow = UndefinedOutputJsonAccessWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete with a rejection event
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    assert terminal_event.error.code == WorkflowErrorCode.NODE_EXECUTION

    assert "Cannot get field" in terminal_event.error.message
    assert "field" in terminal_event.error.message
