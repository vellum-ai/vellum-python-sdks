from vellum.workflows.events.types import WorkflowEventType

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
        event_types={WorkflowEventType.NODE, WorkflowEventType.WORKFLOW},
    )
    events = list(stream)

    # THEN we see the expected events in the correct order
    assert events[0].name == "workflow.execution.initiated"

    assert events[1].name == "node.execution.initiated"
    assert events[1].node_definition == InnerNode
    assert events[1].model_dump(mode="json")["body"]["node_definition"] == {
        "name": "TryNode",
        "module": ["tests", "workflows", "stream_try_node_annotation", "workflow", "InnerNode", "<adornment>"],
    }

    assert events[2].name == "node.execution.streaming"
    assert events[2].output.name == "processed"
    assert events[2].output.is_initiated

    assert events[3].name == "workflow.execution.streaming"
    assert events[3].output.name == "final_value"
    assert events[3].output.is_initiated

    assert events[4].name == "node.execution.streaming"
    assert events[4].output.delta == "apple apple"

    assert events[5].name == "workflow.execution.streaming"
    assert events[5].output.delta == "apple apple"

    assert events[6].name == "node.execution.streaming"
    assert events[6].output.name == "processed"
    assert events[6].output.delta == "banana banana"

    assert events[7].name == "workflow.execution.streaming"
    assert events[7].output.delta == "banana banana"

    assert events[8].name == "node.execution.streaming"
    assert events[8].output.delta == "cherry cherry"

    assert events[9].name == "workflow.execution.streaming"
    assert events[9].output.delta == "cherry cherry"

    assert events[10].name == "node.execution.streaming"
    assert events[10].output.value == ["apple apple", "banana banana", "cherry cherry"]

    assert events[11].name == "workflow.execution.streaming"
    assert events[11].output.value == ["apple apple", "banana banana", "cherry cherry"]

    assert events[12].name == "node.execution.fulfilled"
    assert events[12].outputs.processed == ["apple apple", "banana banana", "cherry cherry"]

    assert events[13].name == "workflow.execution.fulfilled"
    assert events[13].outputs.final_value == ["apple apple", "banana banana", "cherry cherry"]

    assert len(events) == 14
