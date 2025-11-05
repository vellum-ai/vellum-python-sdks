from uuid import UUID

from tests.workflows.try_node_execute_wrapped_node.workflow import TryNodeExecuteWrappedNodeWorkflow, WrappedNode


def test_execute_try_node_wrapped_node_by_id():
    """
    Test that we can execute a workflow starting from a Try Node wrapped node
    by passing its ID to entrypoint_nodes.
    """

    # GIVEN a workflow with a Try Node wrapped node
    workflow = TryNodeExecuteWrappedNodeWorkflow()

    wrapped_node_id = WrappedNode.__id__
    assert isinstance(wrapped_node_id, UUID)

    final_event = workflow.run(entrypoint_nodes=[wrapped_node_id])

    assert final_event.name == "workflow.execution.fulfilled"

    assert final_event.outputs.final_result == "inner_node_executed"

    assert final_event.outputs.error is None


def test_execute_try_node_wrapped_node_by_class():
    """
    Test that we can execute a workflow starting from a Try Node wrapped node
    by passing the node class to entrypoint_nodes.
    """

    # GIVEN a workflow with a Try Node wrapped node
    workflow = TryNodeExecuteWrappedNodeWorkflow()

    final_event = workflow.run(entrypoint_nodes=[WrappedNode])

    assert final_event.name == "workflow.execution.fulfilled"

    assert final_event.outputs.final_result == "inner_node_executed"

    assert final_event.outputs.error is None
