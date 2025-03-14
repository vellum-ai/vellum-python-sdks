import pytest

from pytest_mock import MockerFixture

from tests.workflows.run_from_workflow.workflow import NextNode, RunFromPreviousWorkflow


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
