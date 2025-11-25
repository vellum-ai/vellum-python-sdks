from tests.workflows.basic_regular_exception.workflow import BasicRegularExceptionWorkflow


def test_run_workflow__api_error_has_stacktrace():
    """
    Tests that an ApiError (not NodeException) produces a stacktrace in the rejection event.
    """

    # GIVEN a workflow that references a node that raises an ApiError
    workflow = BasicRegularExceptionWorkflow()

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete with a rejection event
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the stacktrace should contain meaningful stack trace information
    assert terminal_event.body.stacktrace is not None
    assert "ApiError" in terminal_event.body.stacktrace
    assert "Regular exception occurred" in terminal_event.body.stacktrace
    assert "workflow.py" in terminal_event.body.stacktrace
    assert "in run" in terminal_event.body.stacktrace
