import pytest

from pytest_mock import MockerFixture

from vellum.workflows.constants import undefined
from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode
from vellum.workflows.workflows.event_filters import all_workflow_event_filter

from tests.workflows.basic_try_node.workflow import SimpleTryExample, StartNode


@pytest.fixture
def mock_random_int(mocker: MockerFixture):
    base_module = __name__.split(".")[:-2]
    return mocker.patch(".".join(base_module + ["workflow", "random", "randint"]))


def test_run_workflow__happy_path(mock_random_int):
    # GIVEN a workflow that references a try node annotation
    workflow = SimpleTryExample()

    # AND the underlying node succeeds
    mock_random_int.return_value = 8

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the expected value
    assert terminal_event.outputs.final_value == 8


def test_run_workflow__catch_error(mock_random_int):
    # GIVEN a workflow that references a try node annotation
    workflow = SimpleTryExample()

    # AND the underlying node fails
    mock_random_int.return_value = 2

    # WHEN the workflow is run
    terminal_event = workflow.run()

    # THEN the workflow should complete successfully
    assert terminal_event.name == "workflow.execution.fulfilled", terminal_event

    # AND the output should match the expected value
    assert terminal_event.outputs.error == WorkflowError(
        message="This is a flaky node", code=WorkflowErrorCode.NODE_EXECUTION
    )
    assert terminal_event.outputs.final_value is undefined


def test_stream_workflow__catch_error(mock_random_int):
    """
    Verify that when the inner node fails, the inner node rejects, the inner workflow rejects,
    the outer node fulfills, and the outer workflow fulfills.
    """

    # GIVEN a workflow that references a try node annotation
    workflow = SimpleTryExample()

    # AND the underlying node fails
    mock_random_int.return_value = 2

    # WHEN the workflow is streamed
    stream = workflow.stream(event_filter=all_workflow_event_filter)
    events = list(stream)

    InnerWorkflow = StartNode.subworkflow.instance
    WrappedNode = StartNode.__wrapped_node__

    # AND the inner node should reject
    inner_node_rejected_events = [
        e for e in events if e.name == "node.execution.rejected" and e.node_definition == WrappedNode
    ]
    assert len(inner_node_rejected_events) == 1
    assert inner_node_rejected_events[0].error.code == WorkflowErrorCode.NODE_EXECUTION
    assert inner_node_rejected_events[0].error.message == "This is a flaky node"

    # AND the inner workflow should reject
    inner_workflow_rejected_events = [
        e for e in events if e.name == "workflow.execution.rejected" and e.workflow_definition == InnerWorkflow
    ]
    assert len(inner_workflow_rejected_events) == 1
    assert inner_workflow_rejected_events[0].error.code == WorkflowErrorCode.NODE_EXECUTION
    assert inner_workflow_rejected_events[0].error.message == "This is a flaky node"

    # AND the outer node (TryNode) should fulfill
    outer_node_fulfilled_events = [
        e for e in events if e.name == "node.execution.fulfilled" and e.node_definition == StartNode
    ]
    assert len(outer_node_fulfilled_events) == 1
    assert outer_node_fulfilled_events[0].outputs.error == WorkflowError(
        message="This is a flaky node", code=WorkflowErrorCode.NODE_EXECUTION
    )

    # AND the outer workflow should fulfill
    outer_workflow_fulfilled_events = [
        e for e in events if e.name == "workflow.execution.fulfilled" and e.workflow_definition == SimpleTryExample
    ]
    assert len(outer_workflow_fulfilled_events) == 1
    assert outer_workflow_fulfilled_events[0].outputs.error == WorkflowError(
        message="This is a flaky node", code=WorkflowErrorCode.NODE_EXECUTION
    )
    assert outer_workflow_fulfilled_events[0].outputs.final_value is undefined

    # AND the events should occur in the correct order
    inner_node_rejected_index = events.index(inner_node_rejected_events[0])
    inner_workflow_rejected_index = events.index(inner_workflow_rejected_events[0])
    outer_node_fulfilled_index = events.index(outer_node_fulfilled_events[0])
    outer_workflow_fulfilled_index = events.index(outer_workflow_fulfilled_events[0])

    assert inner_node_rejected_index < inner_workflow_rejected_index
    assert inner_workflow_rejected_index < outer_node_fulfilled_index
    assert outer_node_fulfilled_index < outer_workflow_fulfilled_index
