import pytest

from tests.workflows.port_split_await_all.workflow import Inputs, PortSplitAwaitAllWorkflow


@pytest.mark.parametrize("condition", [True, False])
def test_port_split_await_all__should_trigger_merge_node(condition: bool):
    """
    Tests that an AWAIT_ALL merge node triggers when a single upstream node
    with multiple output ports invokes it via one of those ports.
    """

    workflow = PortSplitAwaitAllWorkflow()

    terminal_event = workflow.run(inputs=Inputs(condition=condition))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    assert terminal_event.outputs.final == "completed"
