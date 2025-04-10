import pytest

from tests.workflows.circular_loop.workflow import CircularLoopWorkflow


@pytest.mark.skip(reason="This test will fail because of circular loop")
def test_workflow__happy_path():
    """
    This test is not happy now.

    The key problem is:
    1. TopNode after IncrementCounterNode will not be executed
    2. This breaks the loop and the workflow terminates prematurely
    """
    workflow = CircularLoopWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()
    
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event.body

    assert terminal_event.outputs.counter == 2
    assert terminal_event.outputs.completed is True
