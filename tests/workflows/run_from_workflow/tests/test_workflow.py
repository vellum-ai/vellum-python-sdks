import pytest

from pytest_mock import MockerFixture

from tests.workflows.run_from_workflow.workflow import NextNode, RunFromPreviousWorkflow, StartNode


@pytest.fixture
def mock_random_int(mocker: MockerFixture):
    base_module = __name__.split(".")[:-2]
    return mocker.patch(".".join(base_module + ["workflow", "random", "randint"]))


def test_run_workflow__happy_path(mock_random_int):
    # GIVEN a node that fails non-deterministically the first time, but succeeds the second
    mock_random_int.side_effect = iter([99, 42])

    # AND a workflow the runs this node
    workflow = RunFromPreviousWorkflow()

    # AND we run it once the first time with a failure
    terminal_event = workflow.run()
    assert terminal_event.name == "workflow.execution.rejected"

    # WHEN the workflow is resumed from the node that failed
    terminal_event = workflow.run(entrypoint_nodes=[NextNode])

    # THEN the workflow should be fulfilled
    assert terminal_event.name == "workflow.execution.fulfilled"

    # AND the final value should be as expected
    assert terminal_event.outputs == {"final_value": 47}


def test_stream_workflow__happy_path(mock_random_int):
    """
    Runs a workflow that has access to an external emitter and resolver. The test runs
    the workflow twice, with the second run resuming from the first run as a stream, to
    make assertions about initiated events.
    """

    # GIVEN a node that fails non-deterministically the first time, but succeeds the second
    mock_random_int.side_effect = iter([99, 42])

    # AND a workflow with external emitters and resolvers that runs this node
    workflow = RunFromPreviousWorkflow()

    # AND we run it once the first time with a failure
    terminal_event = workflow.run()
    assert terminal_event.name == "workflow.execution.rejected"

    # WHEN the workflow is restarted from the node that failed
    stream = workflow.stream(entrypoint_nodes=[NextNode])
    events = list(stream)

    # THEN the workflow should be fulfilled
    assert events[-1].name == "workflow.execution.fulfilled"

    # AND the final value should be as expected
    assert events[-1].outputs == {"final_value": 47}

    # AND the workflow execution should have the same span id
    assert events[-1].span_id == events[-1].span_id

    # AND the workflow execution's initiated event should have the initial state
    initiated_event = events[0]
    assert initiated_event.name == "workflow.execution.initiated"
    assert initiated_event.initial_state is not None
    assert initiated_event.initial_state.meta.span_id == events[-1].span_id
    assert initiated_event.initial_state.meta.node_outputs == {StartNode.Outputs.next_value: 5}
