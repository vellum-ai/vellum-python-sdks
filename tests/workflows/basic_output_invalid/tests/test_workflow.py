from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.basic_output_invalid.workflow import BasicInvalidOutputWorkflow


def test_workflow__happy_path():
    # GIVEN a workflow that passes invalid output
    workflow = BasicInvalidOutputWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should be rejected
    assert terminal_event.name == "workflow.execution.rejected", terminal_event
    assert terminal_event.error.message == "Unexpected outputs: {'invalid_output'}"
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_OUTPUTS
