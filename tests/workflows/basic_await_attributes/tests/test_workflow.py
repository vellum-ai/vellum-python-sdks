from tests.workflows.basic_await_attributes.workflow import BasicAwaitAttributesWorkflow


def test_workflow__happy_path():
    """
    This test ensures that the Workflow completes successfully with proper AWAIT_ATTRIBUTES behavior.
    """

    # GIVEN a Workflow with an AwaitAttributesNode
    workflow = BasicAwaitAttributesWorkflow()

    # WHEN the Workflow is run
    final_event = workflow.run()

    # THEN the Workflow completes successfully
    assert final_event.name == "workflow.execution.fulfilled"
    assert final_event.outputs.final_value == 2
