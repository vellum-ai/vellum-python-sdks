from uuid import UUID

from tests.workflows.try_node_execute_wrapped_node.workflow import TryNodeExecuteWrappedNodeWorkflow, WrappedNode


def test_execute_try_node_wrapped_node_by_id():
    """
    Test that we can execute the inner wrapped node of a Try Node adornment
    using run_node and verify it executes with the correct ID.
    """

    # GIVEN a workflow with a Try Node wrapped node
    workflow = TryNodeExecuteWrappedNodeWorkflow()

    # AND we get the inner wrapped node's ID and class
    inner_node_id = WrappedNode.__wrapped_node__.__id__
    inner_node_class = WrappedNode.__wrapped_node__
    assert isinstance(inner_node_id, UUID)

    events = list(workflow.run_node(inner_node_class))
    final_event = events[-1]

    assert final_event.name == "node.execution.fulfilled"

    assert final_event.body.node_definition.__id__ == inner_node_id

    assert final_event.outputs.result == "inner_node_executed"
