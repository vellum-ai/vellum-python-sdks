from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.multi_output_node_streaming.workflow import Inputs, MultiOutputNodeStreaming, StreamingNode


def test_run_workflow__happy_path():
    # GIVEN a simple workflow that references a node with a streaming node that emits 3 events
    workflow = MultiOutputNodeStreaming()

    # WHEN the workflow is run
    inputs = Inputs(foo="Hello")
    events = list(workflow.stream(event_filter=all_workflow_event_filter, inputs=inputs))

    # THEN there should only be 1 snapshot event
    snapshot_events = [event for event in events if event.name == "workflow.execution.snapshotted"]
    assert len(snapshot_events) == 1

    # AND the snapshot should have both fulfilled outputs
    assert snapshot_events[0].state.meta.node_outputs[StreamingNode.Outputs.stream] == [
        "Hello, world! 0",
        "Hello, world! 1",
        "Hello, world! 2",
    ]
    assert snapshot_events[0].state.meta.node_outputs[StreamingNode.Outputs.other_output] == "foo"
