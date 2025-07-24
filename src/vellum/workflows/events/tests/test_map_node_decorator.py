import logging
from unittest.mock import patch
from uuid import uuid4

from vellum.workflows.context import execution_context
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from ..context import get_monitoring_execution_context
from .workflow import Inputs, SimpleMapExample

logger = logging.getLogger(__name__)


def test_map_node_monitoring_context_flow():
    """Test that monitoring creates the correct workflow→node→subworkflow context hierarchy using streamed events."""

    # Patch the old context functions to use the new monitoring system -- just for getting current execution context
    with patch("vellum.workflows.context.get_execution_context", side_effect=get_monitoring_execution_context):
        workflow = SimpleMapExample()
        inputs = Inputs(fruits=["apple", "banana", "cherry"])

        with execution_context(trace_id=uuid4()):
            events = list(workflow.stream(inputs=inputs, event_filter=all_workflow_event_filter))

    # Verify workflow succeeded
    assert len(events) >= 2
    assert events[0].name == "workflow.execution.initiated"
    assert events[-1].name == "workflow.execution.fulfilled"

    # Verify expected outputs
    if hasattr(events[-1], "outputs"):
        expected_outputs = [5, 7, 8]  # len("apple")+0, len("banana")+1, len("cherry")+2
        assert events[-1].outputs == {"final_value": expected_outputs}

    # Collect all events with parent context
    events_with_parent = [event for event in events if event.parent is not None]

    assert len(events_with_parent) > 0, "Expected at least some events with parent context"

    # Filter for node events (including map node and subworkflow events)
    node_events = [event for event in events if event.name.startswith("node.")]
    assert len(node_events) > 0, "Expected at least some node events"

    # Filter for workflow events from subworkflows
    subworkflow_events = [event for event in events if event.name.startswith("workflow.") and event.parent is not None]
    assert len(subworkflow_events) > 0, "Expected subworkflow events with parent context"

    # Verify main workflow node events have the correct parent
    main_workflow_node_events = [event for event in node_events if event.parent and event.parent.type == "WORKFLOW"]
    assert len(main_workflow_node_events) > 0, "Expected node events with main workflow as parent"

    for event in main_workflow_node_events:
        assert event.parent
        assert event.parent.type == "WORKFLOW", "Node event parent should be workflow"

    # Verify subworkflow events have the correct parent context hierarchy
    for event in subworkflow_events:
        assert event.parent is not None, "Subworkflow event should have parent context"
        # The parent could be either a node (MapFruitsNode) or workflow depending on execution context
        parent_type = event.parent.type
        assert parent_type in ["WORKFLOW_NODE"], f"Unexpected parent type: {parent_type}"
