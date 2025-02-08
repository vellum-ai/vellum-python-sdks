from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.invalid_port_resolution.workflow import InvalidPortResolutionWorkflow


def test_workflow__expected_path():
    """
    Confirm that we raise the correct error when the port resolution is invalid.
    """

    # GIVEN a workflow with an invalid port description
    workflow = InvalidPortResolutionWorkflow()

    # WHEN the workflow is executed
    final_event = workflow.run()

    # THEN the workflow raises the correct error
    assert final_event.name == "workflow.execution.rejected"
    assert final_event.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert final_event.error.message == "Invalid port `foo`: Bad"
