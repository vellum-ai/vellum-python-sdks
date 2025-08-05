from vellum.workflows.nodes.utils import ADORNMENT_MODULE_NAME
from vellum.workflows.types.definition import CodeResourceDefinition, VellumCodeResourceDefinition
from vellum.workflows.utils.uuids import uuid4_from_hash
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.stream_retry_node_annotation.workflow import InnerNode, Inputs, StreamingRetryExample


def test_workflow_stream__happy_path():
    """
    Ensure that we can stream the events of a Workflow that contains a RetryNode,
    with a particular focus on ensuring that the definitions of the events are correct.
    """

    # GIVEN a Workflow with a RetryNode
    workflow = StreamingRetryExample()

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
    workflow_initiated_events = [e for e in events if e.name == "workflow.execution.initiated"]
    assert workflow_initiated_events[0].workflow_definition == StreamingRetryExample
    assert workflow_initiated_events[0].parent is not None
    assert workflow_initiated_events[0].parent.type == "EXTERNAL"
    assert workflow_initiated_events[1].workflow_definition == InnerWorkflow

    assert workflow_initiated_events[1].parent is not None
    assert workflow_initiated_events[1].parent.type == "WORKFLOW_NODE"
    assert workflow_initiated_events[1].parent.node_definition == CodeResourceDefinition.encode(InnerNode)
    assert len(workflow_initiated_events) == 2

    # node initiated events
    node_initiated_events = [e for e in events if e.name == "node.execution.initiated"]
    assert node_initiated_events[0].node_definition == InnerNode
    assert node_initiated_events[0].model_dump(mode="json")["body"]["node_definition"] == {
        "name": "RetryNode",
        "id": str(uuid4_from_hash(InnerNode.__qualname__)),
        "module": [
            "tests",
            "workflows",
            "stream_retry_node_annotation",
            "workflow",
            "InnerNode",
            ADORNMENT_MODULE_NAME,
        ],
    }
    assert node_initiated_events[0].parent is not None
    assert node_initiated_events[0].parent.type == "WORKFLOW"
    assert node_initiated_events[0].parent.workflow_definition == VellumCodeResourceDefinition.encode(
        StreamingRetryExample
    )
    assert node_initiated_events[1].node_definition == WrappedNode
    assert node_initiated_events[1].parent is not None
    assert node_initiated_events[1].parent.type == "WORKFLOW"
    assert node_initiated_events[1].parent.workflow_definition == VellumCodeResourceDefinition.encode(InnerWorkflow)
    assert len(node_initiated_events) == 2

    # inner node streaming events
    inner_node_streaming_events = [
        e for e in events if e.name == "node.execution.streaming" and e.node_definition == WrappedNode
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
        e for e in events if e.name == "workflow.execution.streaming" and e.workflow_definition == InnerWorkflow
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

    # No outer node streaming events
    outer_node_streaming_events = [
        e for e in events if e.name == "node.execution.streaming" and e.node_definition == InnerNode
    ]
    assert len(outer_node_streaming_events) == 0

    # outer workflow streaming events
    outer_workflow_streaming_events = [
        e for e in events if e.name == "workflow.execution.streaming" and e.workflow_definition == StreamingRetryExample
    ]
    assert outer_workflow_streaming_events[0].output.value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(outer_workflow_streaming_events) == 1

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
    workflow_fulfilled_events = [e for e in events if e.name == "workflow.execution.fulfilled"]
    assert workflow_fulfilled_events[0].workflow_definition == InnerWorkflow
    assert workflow_fulfilled_events[0].outputs == {"processed": ["apple apple", "banana banana", "cherry cherry"]}
    assert workflow_fulfilled_events[1].workflow_definition == StreamingRetryExample
    assert workflow_fulfilled_events[1].outputs.final_value == [
        "apple apple",
        "banana banana",
        "cherry cherry",
    ]
    assert len(workflow_fulfilled_events) == 2

    # workflow snapshotted events
    workflow_snapshotted_events = [e for e in events if e.name == "workflow.execution.snapshotted"]
    assert len(workflow_snapshotted_events) == 3

    # AND the total number of events is correct
    assert len(events) == 22
