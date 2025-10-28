import pytest

from vellum.workflows.constants import undefined

from tests.workflows.port_split_await_all.workflow import Inputs, PortSplitAwaitAllWorkflow


@pytest.mark.parametrize("condition", [True, False])
def test_port_split_await_all__should_not_trigger_merge_node(condition: bool):
    """
    Tests that an AWAIT_ALL merge node does NOT trigger when a single upstream node
    with mutually exclusive ports invokes it. AWAIT_ALL requires all upstream dependencies
    to invoke the node, but with mutually exclusive ports only one can invoke per run.
    """
    workflow = PortSplitAwaitAllWorkflow()

    # WHEN the workflow is run with either condition
    terminal_event = workflow.run(inputs=Inputs(condition=condition))

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the merge node should NOT trigger, leaving final as undefined
    assert terminal_event.outputs.final is undefined
