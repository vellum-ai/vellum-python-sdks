from tests.workflows.retry_node_await_attributes.workflow import RetryWrappedAwaitAttributesWorkflow


def test_retry_node_await_attributes_timing():
    """
    Test that demonstrates the issue where RetryNode-wrapped nodes don't properly
    respect AWAIT_ALL merge behavior, causing them to execute before all dependencies
    are ready.
    """
    # GIVEN a workflow with a RetryNode-wrapped prompt that should wait for both slow and fast nodes
    workflow = RetryWrappedAwaitAttributesWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the execution count should be 1 for each node
    assert terminal_event.outputs.prompt_execution_count == 1
    assert terminal_event.outputs.slow_execution_count == 1
    assert terminal_event.outputs.fast_execution_count == 1
