from tests.workflows.concurrent_map_execution.workflow import ConcurrentMapExecutionWorkflow, Inputs


def test_concurrent_map_execution():
    """Test using the actual map workflow pattern - should fail with delattr bug."""

    # GIVEN a workflow with a map node that has a subworkflow with a code execution node
    workflow = ConcurrentMapExecutionWorkflow()

    inputs = Inputs(arr=["a"] * 20)

    # WHEN the workflow is run
    terminal_event = workflow.run(inputs=inputs)

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled"
    assert all(output == 1 for output in terminal_event.outputs.final_output)
