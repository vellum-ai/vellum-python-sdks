import pytest
from uuid import uuid4

from vellum.workflows.errors.types import WorkflowErrorCode
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.nodes.bases import BaseNode
from vellum.workflows.outputs import BaseOutputs
from vellum.workflows.resolvers.base import BaseWorkflowResolver
from vellum.workflows.runner.runner import WorkflowRunner
from vellum.workflows.workflows.base import BaseWorkflow


class FailingResolver(BaseWorkflowResolver):
    """A resolver that always fails to load state."""

    def load_state(self, previous_execution_id=None):
        return None

    def get_latest_execution_events(self):
        return iter([])

    def get_state_snapshot_history(self):
        return iter([])


class ExceptionThrowingResolver(BaseWorkflowResolver):
    """A resolver that throws an exception when trying to load state."""

    def load_state(self, previous_execution_id=None):
        raise Exception("Resolver failed")

    def get_latest_execution_events(self):
        return iter([])

    def get_state_snapshot_history(self):
        return iter([])


class TestNode(BaseNode):
    class Outputs(BaseOutputs):
        value: str

    def run(self) -> Outputs:
        return self.Outputs(value="test")


class TestWorkflowWithFailingResolver(BaseWorkflow):
    graph = TestNode
    resolvers = [FailingResolver()]


class TestWorkflowWithExceptionThrowingResolver(BaseWorkflow):
    graph = TestNode
    resolvers = [ExceptionThrowingResolver()]


class TestWorkflowWithMultipleFailingResolvers(BaseWorkflow):
    graph = TestNode
    resolvers = [FailingResolver(), ExceptionThrowingResolver()]


class TestWorkflowWithNoResolvers(BaseWorkflow):
    graph = TestNode
    resolvers = []


def test_workflow_initialization_exception_when_resolver_returns_none():
    """
    Tests that WorkflowInitializationException is raised when resolver returns None.
    """

    workflow = TestWorkflowWithFailingResolver()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "All resolvers failed to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS

    assert exc_info.value.definition == TestWorkflowWithFailingResolver


def test_workflow_initialization_exception_when_resolver_throws_exception():
    """
    Tests that WorkflowInitializationException is raised when resolver throws an exception.
    """

    workflow = TestWorkflowWithExceptionThrowingResolver()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "All resolvers failed to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS


def test_workflow_initialization_exception_when_multiple_resolvers_fail():
    """
    Tests that WorkflowInitializationException is raised when multiple resolvers all fail.
    """

    workflow = TestWorkflowWithMultipleFailingResolvers()

    previous_execution_id = str(uuid4())

    with pytest.raises(WorkflowInitializationException) as exc_info:
        WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert "All resolvers failed to load initial state" in str(exc_info.value)

    assert exc_info.value.code == WorkflowErrorCode.INVALID_INPUTS


def test_no_exception_when_no_resolvers_configured():
    """
    Tests that no exception is raised when workflow has no resolvers configured.
    """

    workflow = TestWorkflowWithNoResolvers()

    previous_execution_id = str(uuid4())

    runner = WorkflowRunner(workflow=workflow, previous_execution_id=previous_execution_id)

    assert runner is not None

    assert set(runner._entrypoints) == set(workflow.get_entrypoints())


def test_no_exception_when_no_previous_execution_id():
    """
    Tests that no exception is raised when no previous execution ID is provided.
    """

    workflow = TestWorkflowWithFailingResolver()

    runner = WorkflowRunner(workflow=workflow)

    assert runner is not None

    assert runner._initial_state is not None
