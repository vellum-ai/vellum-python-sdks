import logging
from uuid import uuid4

from vellum.workflows import BaseWorkflow
from vellum.workflows.context import execution_context
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter


class StartNode(BaseNode):
    pass


class TrivialWorkflow(BaseWorkflow):
    graph = StartNode


logger = logging.getLogger(__name__)


def test_basic_workflow_monitoring_context_flow():
    """Test that monitoring creates the correct workflow→node context hierarchy using streamed events.
    What's missing:
    - span_id from previous event mapping to parent context
    """

    workflow = TrivialWorkflow()

    with execution_context(trace_id=uuid4()):
        events = list(workflow.stream(event_filter=all_workflow_event_filter))

    # Verify workflow succeeded
    assert len(events) >= 2
    assert events[0].name == "workflow.execution.initiated"
    assert events[-1].name == "workflow.execution.fulfilled"

    # Collect all events with parent context
    events_with_parent = [event for event in events if event.parent is not None]

    assert len(events_with_parent) > 0, "Expected at least some events with parent context"

    # Filter for node events
    node_events = [event for event in events if event.name.startswith("node.")]
    assert len(node_events) > 0, "Expected at least some node events"

    # Verify each node event has the workflow as its parent context
    for event in node_events:
        assert event.parent is not None, "Node event should have parent context"
        assert event.parent.type == "WORKFLOW", "Node event parent should be workflow"
        assert event.parent.workflow_definition.name == "TrivialWorkflow", "Parent workflow name mismatch"
