from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.multiple_node_adornments.workflow import MultipleNodeAdornmentsExample, StartNode


def test_stream_workflow__happy_path():
    # GIVEN a workflow that references multiple node adornments
    workflow = MultipleNodeAdornmentsExample()

    # WHEN the workflow is streamed
    stream = workflow.stream(event_filter=all_workflow_event_filter)
    events = list(stream)

    # THEN the workflow should initiate in order
    node_initiated_events = [event for event in events if event.name == "node.execution.initiated"]
    assert len(node_initiated_events) == 3
    assert node_initiated_events[0].node_definition == StartNode
    assert node_initiated_events[1].node_definition == StartNode.__wrapped_node__
    assert StartNode.__wrapped_node__
    assert node_initiated_events[2].node_definition == StartNode.__wrapped_node__.__wrapped_node__
