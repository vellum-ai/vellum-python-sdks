import json

from vellum.workflows.state.encoder import DefaultStateEncoder
from vellum.workflows.workflows.event_filters import root_workflow_event_filter

from tests.workflows.custom_node_exception.workflow import CustomNodeExceptionWorkflow


def test_workflow__run_happy_path():
    """
    Tests that a custom node that catches an exception and returns it as an output
    completes successfully.
    """

    workflow = CustomNodeExceptionWorkflow()

    # WHEN we run the workflow
    terminal_event = workflow.run()

    assert terminal_event.name == "workflow.execution.fulfilled"

    assert isinstance(terminal_event.outputs.error_message, Exception)
    assert str(terminal_event.outputs.error_message) == "foo"


def test_workflow__stream_events_end_with_fulfilled():
    """
    Tests that when streaming a workflow with a custom node that catches exceptions,
    the last event is node.execution.fulfilled, not node.execution.initiated.
    Also tests that events can be serialized to JSON.
    """

    workflow = CustomNodeExceptionWorkflow()

    # WHEN we stream the workflow with root_workflow_event_filter to include node events
    events = list(workflow.stream(event_filter=root_workflow_event_filter))

    assert len(events) > 0, "No events were emitted"

    assert events[-1].name == "workflow.execution.fulfilled"

    node_initiated_events = [e for e in events if e.name == "node.execution.initiated"]
    node_fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    event_names = [e.name for e in events]

    assert len(node_initiated_events) == 1, f"Expected exactly 1 node.execution.initiated event. Events: {event_names}"
    assert len(node_fulfilled_events) == 1, f"Expected exactly 1 node.execution.fulfilled event. Events: {event_names}"

    last_two_events = events[-2:]
    for event in last_two_events:
        serialized = json.dumps(event, cls=DefaultStateEncoder)
        assert serialized is not None
        parsed = json.loads(serialized)
        assert parsed is not None
