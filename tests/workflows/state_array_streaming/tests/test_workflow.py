from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.state_array_streaming.workflow import Inputs, StateArrayStreamingWorkflow


def test_stream_workflow__state_array_writes():
    """
    Test that a node writing to state arrays streams the correct events.
    """

    workflow = StateArrayStreamingWorkflow()

    inputs = Inputs(message="Hello")
    events = list(workflow.stream(event_filter=all_workflow_event_filter, inputs=inputs))

    streaming_events = [e for e in events if e.name == "workflow.execution.streaming"]
    final_messages_events = [e for e in streaming_events if e.output.name == "final_messages"]

    assert len(final_messages_events) == 5

    assert final_messages_events[0].output.is_initiated

    assert final_messages_events[1].output.is_streaming
    assert len(final_messages_events[1].output.delta) > 0

    assert final_messages_events[2].output.is_streaming
    assert len(final_messages_events[2].output.delta) > 0

    assert final_messages_events[3].output.is_streaming
    assert len(final_messages_events[3].output.delta) > 0

    assert final_messages_events[4].output.is_fulfilled
    assert len(final_messages_events[4].output.value) == 3
