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

    assert terminal_event.outputs.error_message == "foo"


def test_workflow__stream_events_end_with_fulfilled():
    """
    Tests that when streaming a workflow with a custom node that catches exceptions,
    the last event is node.execution.fulfilled, not node.execution.initiated.
    """

    workflow = CustomNodeExceptionWorkflow()

    # WHEN we stream the workflow
    events = list(workflow.stream())

    assert len(events) > 0, "No events were emitted"

    assert events[-1].name == "workflow.execution.fulfilled"

    node_initiated_events = [e for e in events if e.name == "node.execution.initiated"]
    node_fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    event_names = [e.name for e in events]

    assert len(node_initiated_events) > 0, f"No node.execution.initiated events found. Events: {event_names}"

    assert len(node_fulfilled_events) > 0, f"No node.execution.fulfilled events found. Events: {event_names}"

    for initiated_event in node_initiated_events:
        matching_fulfilled = [
            e for e in node_fulfilled_events if e.body.node_definition == initiated_event.body.node_definition
        ]
        assert len(matching_fulfilled) > 0, (
            f"Node {initiated_event.body.node_definition} was initiated but never fulfilled. " f"Events: {event_names}"
        )
