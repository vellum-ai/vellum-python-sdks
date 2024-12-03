from tests.workflows.basic_await_any.workflow import BasicAwaitAnyWorkflow


def test_workflow__happy_path():
    """
    This test ensures that the Workflow completes successfully with proper AWAIT_ANY behavior.
    """

    # GIVEN a Workflow with an AwaitAnyNode
    workflow = BasicAwaitAnyWorkflow()

    # WHEN the Workflow is run
    final_event = workflow.run()

    # THEN the Workflow completes successfully
    assert final_event.name == "workflow.execution.fulfilled"
    assert final_event.outputs.final_value == 1
