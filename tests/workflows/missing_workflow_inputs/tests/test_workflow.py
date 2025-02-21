from vellum.workflows.errors.types import WorkflowErrorCode

from tests.workflows.missing_workflow_inputs.workflow import MissingInputsWorkflow


def test_run_workflow__happy_path():
    # GIVEN a workflow that has a node referencing an invalid input
    workflow = MissingInputsWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed with a failure
    assert terminal_event.name == "workflow.execution.rejected", terminal_event

    # AND the outputs should be defaulted correctly
    assert terminal_event.error.code == WorkflowErrorCode.INVALID_INPUTS
    assert terminal_event.error.message == "Missing required Workflow input: initial_value"
