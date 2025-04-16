from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_node_streaming.workflow import BasicNodeStreaming, Inputs, StreamingNode


def test_run_workflow__happy_path():
    # GIVEN a simple workflow that references a node with a streaming node that emits 3 events
    workflow = BasicNodeStreaming()

    # WHEN the workflow is run
    inputs = Inputs(foo="Hello")
    events = list(workflow.stream(event_filter=all_workflow_event_filter, inputs=inputs))

    # THEN the workflow should have emitted 14 events
    #
    # This is a very verbose breakdown of all of the events we emit. It embodies the concept that
    # - A workflow is made up of one or more nodes, each of which emit initiated/streaming/fulfilled/rejected states
    # - A node is made up of one or more outputs, each of which emit initiated/streaming/fulfilled/rejected states
    #
    # This allows end users to have the option to either use values as they stream available or use just the end result.
    assert len(events) == 15

    # AND each event should have the expected data
    assert events[0].name == "workflow.execution.initiated"
    assert events[0].inputs.foo == "Hello"

    assert events[1].name == "node.execution.initiated"
    assert events[1].inputs == {StreamingNode.foo: "Hello"}

    assert events[2].name == "node.execution.streaming"
    assert events[2].output.is_initiated
    assert events[2].output.name == "stream"

    assert events[3].name == "workflow.execution.streaming"
    assert events[3].output.is_initiated
    assert events[3].output.name == "outer_stream"

    assert events[4].name == "node.execution.streaming"
    assert events[4].output.is_streaming
    assert events[4].output.name == "stream"
    assert events[4].output.delta == "Hello, world! 0"

    assert events[5].name == "workflow.execution.streaming"
    assert events[5].output.is_streaming
    assert events[5].output.name == "outer_stream"
    assert events[5].output.delta == "Hello, world! 0"

    assert events[6].name == "node.execution.streaming"
    assert events[6].output.is_streaming
    assert events[6].output.name == "stream"
    assert events[6].output.delta == "Hello, world! 1"

    assert events[7].name == "workflow.execution.streaming"
    assert events[7].output.is_streaming
    assert events[7].output.name == "outer_stream"
    assert events[7].output.delta == "Hello, world! 1"

    assert events[8].name == "node.execution.streaming"
    assert events[8].output.is_streaming
    assert events[8].output.name == "stream"
    assert events[8].output.delta == "Hello, world! 2"

    assert events[9].name == "workflow.execution.streaming"
    assert events[9].output.is_streaming
    assert events[9].output.name == "outer_stream"
    assert events[9].output.delta == "Hello, world! 2"

    assert events[10].name == "node.execution.streaming"
    assert events[10].output.is_fulfilled
    assert events[10].output.name == "stream"
    assert events[10].output.value == [
        "Hello, world! 0",
        "Hello, world! 1",
        "Hello, world! 2",
    ]

    assert events[11].name == "workflow.execution.streaming"
    assert events[11].output.is_fulfilled
    assert events[11].output.name == "outer_stream"
    assert events[11].output.value == [
        "Hello, world! 0",
        "Hello, world! 1",
        "Hello, world! 2",
    ]

    assert events[12].name == "workflow.execution.snapshotted"

    assert events[13].name == "node.execution.fulfilled"
    assert events[13].outputs.stream == [
        "Hello, world! 0",
        "Hello, world! 1",
        "Hello, world! 2",
    ]

    assert events[14].name == "workflow.execution.fulfilled"
    assert events[14].outputs.outer_stream == [
        "Hello, world! 0",
        "Hello, world! 1",
        "Hello, world! 2",
    ]
