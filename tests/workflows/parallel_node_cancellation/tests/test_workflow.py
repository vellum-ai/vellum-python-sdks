from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.parallel_node_cancellation.workflow import BottomNode, ParallelNodeCancellationWorkflow, TopNode


def test_parallel_node_cancellation__streaming():
    """
    Tests that when one parallel node fails, the other parallel node receives a rejection event.
    """

    workflow = ParallelNodeCancellationWorkflow()

    stream = workflow.stream(event_filter=all_workflow_event_filter)
    events = list(stream)

    rejection_events = [e for e in events if e.name == "node.execution.rejected"]

    assert len(rejection_events) == 2, f"Expected 2 rejection events, got {len(rejection_events)}"

    top_node_rejection = next((e for e in rejection_events if e.node_definition == TopNode), None)
    bottom_node_rejection = next((e for e in rejection_events if e.node_definition == BottomNode), None)

    assert top_node_rejection is not None, "Expected TopNode rejection event"
    assert bottom_node_rejection is not None, "Expected BottomNode rejection event"

    assert top_node_rejection.error.code == WorkflowErrorCode.USER_DEFINED_ERROR
    assert top_node_rejection.error.message == "Top node failed"

    assert bottom_node_rejection.error.code == WorkflowErrorCode.NODE_CANCELLED
