from tests.workflows.multi_retry_node.workflow import MultiRetryWorkflow


def test_run_workflow__happy_path():
    # GIVEN a workflow that has multiple retry nodes defined
    workflow = MultiRetryWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should have completed successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the outputs should be defaulted correctly
    assert terminal_event.outputs == {"final_result": "Hello World"}
