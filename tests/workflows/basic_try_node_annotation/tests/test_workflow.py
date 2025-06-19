import pytest

from pytest_mock import MockerFixture

from vellum.workflows.errors.types import WorkflowError, WorkflowErrorCode

from tests.workflows.basic_try_node_annotation.workflow import SimpleTryExample


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
    assert terminal_event.outputs == {
        "final_value": WorkflowError(message="This is a flaky node", code=WorkflowErrorCode.NODE_EXECUTION)
    }
