from vellum.workflows.events.types import CodeResourceDefinition, serialize_type_encoder
from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.stream_try_node_annotation.workflow import InnerNode, Inputs, StreamingTryExample


def test_workflow_stream__happy_path():
    """
    Ensure that we can stream the events of a Workflow that contains a TryNode,
    with a particular focus on ensuring that the definitions of the events are correct.
    """

    # GIVEN a Workflow with a TryNode
    workflow = StreamingTryExample()

    # WHEN we stream the events of the Workflow
    stream = workflow.stream(
        inputs=Inputs(items=["apple", "banana", "cherry"]),
        event_filter=all_workflow_event_filter,
    )
    events = list(stream)

    # THEN we see the expected events in the correct relative order
    InnerWorkflow = InnerNode.subworkflow.instance
    WrappedNode = InnerNode.__wrapped_node__

    # workflow initiated events
    workflow_initiated_events = [
        e for e in events if e.name == "workflow.execution.initiated"
    ]
    assert workflow_initiated_events[0].workflow_definition == StreamingTryExample
    assert workflow_initiated_events[0].parent is None
    assert workflow_initiated_events[1].workflow_definition == InnerWorkflow
    # TODO: Try Node Parent Context - https://app.shortcut.com/vellum/story/5601
    # assert workflow_initiated_events[1].parent is not None
    # assert workflow_initiated_events[1].parent.type == "WORKFLOW_NODE"
    # assert workflow_initiated_events[1].parent.node_definition == InnerNode
    assert len(workflow_initiated_events) == 2

    # node initiated events
    node_initiated_events = [e for e in events if e.name == "node.execution.initiated"]
    assert node_initiated_events[0].node_definition == InnerNode
    assert node_initiated_events[0].model_dump(mode="json")["body"][
        "node_definition"
    ] == {
        "name": "TryNode",
        "module": [
            "tests",
            "workflows",
            "stream_try_node_annotation",
            "workflow",
            "InnerNode",
            ADORNMENT_MODULE_NAME,
        ],
    }
    assert node_initiated_events[0].parent is not None
    assert node_initiated_events[0].parent.type == "WORKFLOW"
    assert node_initiated_events[
        0
    ].parent.workflow_definition == CodeResourceDefinition(
        **serialize_type_encoder(StreamingTryExample)
    )
    assert node_initiated_events[1].node_definition == WrappedNode
    assert node_initiated_events[1].parent is not None
    assert node_initiated_events[1].parent.type == "WORKFLOW"
    assert node_initiated_events[
        1
    ].parent.workflow_definition == CodeResourceDefinition(
        **serialize_type_encoder(InnerWorkflow)
    )
    assert len(node_initiated_events) == 2

    # inner node streaming events
    inner_node_streaming_events = [
        e
        for e in events
        if e.name == "node.execution.streaming" and e.node_definition == WrappedNode
    ]
    assert inner_node_streaming_events[0].output.name == "processed"
    assert inner_node_streaming_events[0].output.is_initiated
    assert inner_node_streaming_events[1].output.delta == "apple apple"
    assert inner_node_streaming_events[2].output.delta == "banana banana"
    assert inner_node_streaming_events[3].output.delta == "cherry cherry"
    assert inner_node_streaming_events[4].output.value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(inner_node_streaming_events) == 5

    # inner workflow streaming events
    inner_workflow_streaming_events = [
        e
        for e in events
        if e.name == "workflow.execution.streaming"
        and e.workflow_definition == InnerWorkflow
    ]
    assert inner_workflow_streaming_events[0].output.name == "processed"
    assert inner_workflow_streaming_events[0].output.is_initiated
    assert inner_workflow_streaming_events[1].output.delta == "apple apple"
    assert inner_workflow_streaming_events[2].output.delta == "banana banana"
    assert inner_workflow_streaming_events[3].output.delta == "cherry cherry"
    assert inner_workflow_streaming_events[4].output.value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(inner_workflow_streaming_events) == 5

    # outer node streaming events
    outer_node_streaming_events = [
        e
        for e in events
        if e.name == "node.execution.streaming" and e.node_definition == InnerNode
    ]
    assert outer_node_streaming_events[0].output.name == "processed"
    assert outer_node_streaming_events[0].output.is_initiated
    assert outer_node_streaming_events[1].output.delta == "apple apple"
    assert outer_node_streaming_events[2].output.delta == "banana banana"
    assert outer_node_streaming_events[3].output.delta == "cherry cherry"
    assert outer_node_streaming_events[4].output.value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(outer_node_streaming_events) == 5

    # outer workflow streaming events
    outer_workflow_streaming_events = [
        e
        for e in events
        if e.name == "workflow.execution.streaming"
        and e.workflow_definition == StreamingTryExample
    ]
    assert outer_workflow_streaming_events[0].output.name == "final_value"
    assert outer_workflow_streaming_events[0].output.is_initiated
    assert outer_workflow_streaming_events[1].output.delta == "apple apple"
    assert outer_workflow_streaming_events[2].output.delta == "banana banana"
    assert outer_workflow_streaming_events[3].output.delta == "cherry cherry"
    assert outer_workflow_streaming_events[4].output.value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(outer_workflow_streaming_events) == 5

    # node fulfilled events
    node_fulfilled_events = [e for e in events if e.name == "node.execution.fulfilled"]
    assert node_fulfilled_events[0].node_definition == WrappedNode
    assert node_fulfilled_events[0].outputs.processed == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert node_fulfilled_events[1].node_definition == InnerNode
    assert node_fulfilled_events[1].outputs.processed == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(node_fulfilled_events) == 2

    # workflow fulfilled events
    workflow_fulfilled_events = [
        e for e in events if e.name == "workflow.execution.fulfilled"
    ]
    assert workflow_fulfilled_events[0].workflow_definition == InnerWorkflow
    assert workflow_fulfilled_events[0].outputs == {
        "processed": ["apple apple", "banana banana", "cherry cherry"]
    }
    assert workflow_fulfilled_events[1].workflow_definition == StreamingTryExample
    assert workflow_fulfilled_events[1].outputs.final_value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(workflow_fulfilled_events) == 2

    assert len(events) == 28
