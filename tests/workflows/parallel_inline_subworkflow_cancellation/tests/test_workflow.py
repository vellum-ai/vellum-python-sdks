import pytest

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.parallel_inline_subworkflow_cancellation.workflow import (
    FastFailingNode,
    ParallelInlineSubworkflowCancellationWorkflow,
    SlowInlineSubworkflowNode,
    SlowNode,
    SlowSubworkflow,
)


def test_parallel_inline_subworkflow_cancellation__streaming():
    """
    Tests that when one parallel node fails, the other parallel inline subworkflow node
    receives cancellation events, including cancellation events for the nested workflow
    and its inner nodes.
    """

    workflow = ParallelInlineSubworkflowCancellationWorkflow()

    stream = workflow.stream(event_filter=all_workflow_event_filter)
    events = list(stream)
    workflow.join()

    rejection_events = [e for e in events if e.name == "node.execution.rejected"]

    assert (
        len(rejection_events) == 3
    ), f"Expected 3 rejection events, got {[e.node_definition.__name__ for e in rejection_events]}"

    fast_failing_rejection = next((e for e in rejection_events if e.node_definition == FastFailingNode), None)
    assert fast_failing_rejection is not None, "Expected FastFailingNode rejection event"
    assert fast_failing_rejection.error.code == WorkflowErrorCode.USER_DEFINED_ERROR
    assert fast_failing_rejection.error.message == "Fast node failed"

    slow_subworkflow_rejection = next(
        (e for e in rejection_events if e.node_definition == SlowInlineSubworkflowNode), None
    )
    assert slow_subworkflow_rejection is not None, "Expected SlowInlineSubworkflowNode rejection event"
    assert slow_subworkflow_rejection.error.code == WorkflowErrorCode.NODE_CANCELLED

    slow_node_rejection = next((e for e in rejection_events if e.node_definition == SlowNode), None)
    assert slow_node_rejection is not None, "Expected SlowNode rejection event"
    assert slow_node_rejection.error.code == WorkflowErrorCode.NODE_CANCELLED

    workflow_rejection_events = [e for e in events if e.name == "workflow.execution.rejected"]

    assert (
        len(workflow_rejection_events) >= 2
    ), f"Expected at least 2 workflow rejection events, got {len(workflow_rejection_events)}"

    nested_workflow_rejection = next(
        (e for e in workflow_rejection_events if e.workflow_definition == SlowSubworkflow), None
    )
    assert nested_workflow_rejection is not None, "Expected SlowSubworkflow rejection event"
    assert nested_workflow_rejection.error.code == WorkflowErrorCode.WORKFLOW_CANCELLED

    parent_workflow_rejection = next(
        (
            e
            for e in workflow_rejection_events
            if e.workflow_definition == ParallelInlineSubworkflowCancellationWorkflow
        ),
        None,
    )
    assert (
        parent_workflow_rejection is not None
    ), "Expected ParallelInlineSubworkflowCancellationWorkflow rejection event"
