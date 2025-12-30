from vellum.workflows.errors import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.parallel_node_both_fail.workflow import ParallelNodeBothFailWorkflow


def test_parallel_node_both_fail__streaming():
    """
    Tests that when both parallel nodes fail independently, the workflow is rejected.
    """

    # GIVEN a workflow with two parallel nodes that both fail
    workflow = ParallelNodeBothFailWorkflow()

    # WHEN we stream the workflow events
    stream = workflow.stream(event_filter=all_workflow_event_filter)
    events = list(stream)

    # THEN we should have rejection events for both nodes
    rejection_events = [e for e in events if e.name == "node.execution.rejected"]
    assert len(rejection_events) >= 2, f"Expected at least 2 rejection events, got {len(rejection_events)}"

    # AND the workflow should be rejected (not fulfilled)
    last_event = events[-1]
    assert (
        last_event.name == "workflow.execution.rejected"
    ), f"Expected last event to be workflow rejection, got {last_event.name}"

    # AND the workflow error should be from one of the failing nodes (not NODE_CANCELLED)
    assert last_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert last_event.error.message in ["Left node failed", "Right node failed"]


def test_parallel_node_both_fail__run():
    """
    Tests that when both parallel nodes fail independently, the workflow.run() returns a rejected event.
    """

    # GIVEN a workflow with two parallel nodes that both fail
    workflow = ParallelNodeBothFailWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    # THEN the terminal event should be a workflow rejection
    assert (
        terminal_event.name == "workflow.execution.rejected"
    ), f"Expected workflow rejection, got {terminal_event.name}"

    # AND the workflow error should be from one of the failing nodes (not NODE_CANCELLED)
    assert terminal_event.error.code == WorkflowErrorCode.INTERNAL_ERROR
    assert terminal_event.error.message in ["Left node failed", "Right node failed"]
