from unittest.mock import Mock, patch

from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.state.base import BaseState
from vellum.workflows.workflows.base import BaseWorkflow


class TestInputs(BaseInputs):
    pass


class TestWorkflow(BaseWorkflow[TestInputs, BaseState]):
    pass


def test_workflow_join__calls_runner_join():
    """
    Test that BaseWorkflow.join() calls runner.join() when runner exists.
    """

    workflow = TestWorkflow()

    workflow.run()

    workflow.join()

    assert workflow._current_runner is not None


def test_workflow_join__handles_no_runner():
    """
    Test that BaseWorkflow.join() handles case where no runner exists.
    """

    workflow = TestWorkflow()

    workflow.join()

    assert workflow._current_runner is None


def test_workflow_join__calls_runner_join_method():
    """
    Test that BaseWorkflow.join() actually calls the runner's join method.
    """

    workflow = TestWorkflow()

    with patch.object(workflow, "_current_runner") as mock_runner:
        mock_runner.join = Mock()

        workflow.join()

        mock_runner.join.assert_called_once()
