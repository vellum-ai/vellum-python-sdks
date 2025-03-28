from tests.workflows.missing_workflow_inputs_optional.workflow import OptionalInputsWorkflow


def test_run_workflow__happy_path():
    # GIVEN a workflow that has a node referencing an optional input
    workflow = OptionalInputsWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the outputs should be defaulted correctly
    assert terminal_event.outputs["final_value"] is None
