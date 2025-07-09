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

    assert streaming_events[0].output.is_streaming
    assert streaming_events[0].output.delta == ["Hello - write 1"]

    assert streaming_events[1].output.is_streaming
    assert streaming_events[1].output.delta == ["Hello - write 1", "Hello - write 2"]

    assert streaming_events[2].output.is_streaming
    assert streaming_events[2].output.delta == ["Hello - write 1", "Hello - write 2", "Hello - write 3"]

    assert len(streaming_events) == 3
